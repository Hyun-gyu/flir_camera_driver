// -*-c++-*--------------------------------------------------------------------
// Copyright 2023 Bernd Pfrommer <bernd.pfrommer@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <spinnaker_camera_driver/spinnaker_wrapper.hpp>
#include <set>
#include <sstream>
#include <string>
#include <vector>

namespace
{
bool looks_like_hex_serial(const std::string & serial)
{
  return !serial.empty() &&
         std::all_of(serial.begin(), serial.end(), [](unsigned char c) { return std::isxdigit(c); }) &&
         serial.find_first_of("abcdefABCDEF") != std::string::npos;
}

std::string format_serial(const std::string & serial)
{
  if (!looks_like_hex_serial(serial)) {
    return serial;
  }

  char * end = nullptr;
  errno = 0;
  const unsigned long long value = std::strtoull(serial.c_str(), &end, 16);
  if (errno != 0 || end == nullptr || *end != '\0') {
    return serial;
  }

  return std::to_string(value) + "  # raw: " + serial;
}

std::vector<std::string> get_serials_from_lsusb()
{
  std::vector<std::string> serials;
  std::set<std::string> seen;
  std::unique_ptr<FILE, decltype(&pclose)> pipe(
    popen("lsusb -v -d 1e10:4000 2>/dev/null", "r"), pclose);
  if (!pipe) {
    return serials;
  }

  char buffer[512];
  while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
    const std::string line(buffer);
    if (line.find("iSerial") == std::string::npos) {
      continue;
    }

    std::istringstream stream(line);
    std::string token;
    std::string last_token;
    while (stream >> token) {
      last_token = token;
    }
    if (!last_token.empty() && seen.insert(last_token).second) {
      serials.push_back(last_token);
    }
  }

  return serials;
}
}  // namespace

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  int exit_code = 0;
  try {
    spinnaker_camera_driver::SpinnakerWrapper wrapper(rclcpp::get_logger("list_cameras"));
    wrapper.refreshCameraList();
    auto serials = wrapper.getSerialNumbers();
    if (serials.empty()) {
      serials = get_serials_from_lsusb();
    }

    if (serials.empty()) {
      std::cerr << "No FLIR cameras detected." << std::endl;
      exit_code = 1;
    } else {
      for (const auto & serial : serials) {
        std::cout << format_serial(serial) << std::endl;
      }
    }
  } catch (const std::exception & e) {
    std::cerr << "Failed to query cameras: " << e.what() << std::endl;
    exit_code = 1;
  }

  rclcpp::shutdown();
  return exit_code;
}

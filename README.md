# Face-Matching-System
# 🎯 AI Face Matching System

<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Poppins&size=30&pause=1000&color=00C2FF&center=true&vCenter=true&width=800&lines=Face+Matching+System;AI-Powered+Face+Verification;Real-Time+Similarity+Detection;OpenCV+%7C+MongoDB+%7C+Python" />

<br>

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=for-the-badge&logo=opencv)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-success?style=for-the-badge&logo=mongodb)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

</div>

---

## 🌟 Project Overview

The **AI Face Matching System** is a modern desktop application designed to compare facial images and determine similarity between two individuals in real-time.

The system utilizes advanced computer vision techniques to detect faces, extract facial features, and calculate similarity scores with high accuracy. It provides a professional user interface and secure storage using MongoDB.

---

## 🎥 Demo Preview

<p align="center">
<img src="assets/demo.gif" width="900">
</p>

> Replace `demo.gif` with your actual project recording.

---

# ✨ Key Features

### 🔍 Face Verification
Compare two facial images and determine whether they belong to the same person.

### 📷 Webcam Integration
Capture images directly from a connected webcam.

### 🎯 Similarity Score
Generate accurate similarity percentages.

### 💾 MongoDB Storage
Store and retrieve face embeddings and records securely.

### 🎨 Modern User Interface
Professional GUI built using CustomTkinter.

### ⚡ Real-Time Processing
Fast face detection and comparison.

### 📊 Dashboard Analytics
Monitor verification statistics and records.

### 🔐 Secure Architecture
Local processing ensures privacy and data security.

---

# 🏗️ System Architecture

```text
                ┌────────────────────┐
                │     Webcam/Input    │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Face Detection      │
                │     OpenCV          │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Feature Extraction │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Similarity Engine  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ MongoDB Database   │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ GUI Dashboard      │
                └────────────────────┘

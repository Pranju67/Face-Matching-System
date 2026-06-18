# 🚀 AI Face Recognition Management System

<div align="center">

![Banner](https://img.shields.io/badge/AI-Face%20Recognition-purple?style=for-the-badge)

![React](https://img.shields.io/badge/Frontend-ReactJS-61DAFB?style=for-the-badge\&logo=react)
![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge\&logo=flask)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-13AA52?style=for-the-badge\&logo=mongodb)
![InsightFace](https://img.shields.io/badge/AI-InsightFace-FF6B6B?style=for-the-badge)
![JWT](https://img.shields.io/badge/Auth-JWT-orange?style=for-the-badge)

<br>

### ⚡ Enterprise Grade AI Face Recognition Platform

### Real-Time Recognition • Analytics • User Management • Security

<img src="https://readme-typing-svg.herokuapp.com?font=Poppins&weight=700&size=26&pause=1000&color=A855F7&center=true&vCenter=true&width=700&lines=AI+Face+Recognition+Management+System;Real-Time+Face+Identification;Enterprise+Dashboard+Analytics;InsightFace+Powered+Recognition;React+%2B+Flask+%2B+MongoDB" />

</div>

---

# 🌟 Overview

An enterprise-grade AI-powered Face Recognition Management System built using modern web technologies and advanced facial recognition algorithms.

The platform provides:

✅ Face Registration

✅ Real-Time Face Recognition

✅ User Management

✅ Recognition Analytics

✅ Recognition History

✅ Admin Authentication

✅ Dashboard Monitoring

✅ MongoDB Storage

✅ Report Generation

✅ Enterprise UI/UX

---

# 🎥 Live System Preview

### Dashboard

* Glassmorphism Cards
* Animated Metrics
* Live Statistics
* Real-Time Updates

### Recognition Module

* Webcam Streaming
* Face Detection
* Face Identification
* Similarity Scoring
* Confidence Calculation

### Analytics

* Pie Charts
* Line Charts
* Bar Charts
* Area Charts

### User Management

* Search Users
* Edit User
* Delete User
* Face Information

---

# ✨ Premium UI Features

## Modern Enterprise Design

✔ Black Theme

✔ Neon Purple Glow

✔ Glassmorphism Effects

✔ Blur Backgrounds

✔ Floating Gradients

✔ Animated Cards

✔ Responsive Layout

✔ Mobile Friendly

✔ Smooth Navigation

✔ Professional Components

---

# 🎨 Animations Included

### Framer Motion Animations

### Dashboard

* Fade In
* Slide Up
* Card Hover Glow
* Counter Animations

### Sidebar

* Smooth Collapse
* Expand Animation
* Active Route Indicator

### Tables

* Row Entrance Animation
* Hover Effects

### Analytics

* Chart Loading Animation
* Dynamic Transitions

### Recognition

* Face Detection Glow
* Live Status Updates

---

# 🏗️ System Architecture

```text
┌─────────────────────────────┐
│       React Frontend        │
└──────────────┬──────────────┘
               │
               │ Axios API Calls
               │
┌──────────────▼──────────────┐
│         Flask API           │
└──────────────┬──────────────┘
               │
 ┌─────────────┼─────────────┐
 │             │             │
 ▼             ▼             ▼

MongoDB     JWT Auth    Recognition Engine

                           │
                           ▼

                     InsightFace

                           │
                           ▼

                      Embeddings

                           │
                           ▼

                  Cosine Similarity
```

---

# 🛠 Technology Stack

## Frontend

* React.js
* Vite
* Tailwind CSS
* Framer Motion
* Recharts
* Axios
* React Router DOM
* React Icons
* React Hot Toast

## Backend

* Python Flask
* OpenCV
* InsightFace
* NumPy
* Scikit-Learn
* Joblib
* JWT Authentication
* PyMongo

## Database

* MongoDB Localhost

---

# 📁 Project Structure

```bash
AI-Face-Recognition-System/

├── backend/
│
├── controllers/
│
├── routes/
│
├── services/
│
├── utils/
│
├── models/
│
├── uploads/
│
├── embeddings/
│
├── frontend/
│
├── src/
│
├── components/
│
├── pages/
│
├── layouts/
│
├── hooks/
│
├── services/
│
├── assets/
│
├── public/
│
└── README.md
```

---

# 🔐 Authentication

### Admin Login

Secure JWT Authentication

Features:

* Login
* Logout
* Session Validation
* Protected Routes
* Token Expiry
* Authorization Middleware

---

# 👤 Face Registration Workflow

```text
Open Webcam
      │
      ▼
Capture Face
      │
      ▼
Extract Embedding
      │
      ▼
Save Face Image
      │
      ▼
Store Embedding
      │
      ▼
Save User Details
      │
      ▼
MongoDB
```

---

# 🤖 Face Recognition Workflow

```text
Webcam Feed
      │
      ▼
Detect Face
      │
      ▼
Generate Embedding
      │
      ▼
Load Stored Embeddings
      │
      ▼
Cosine Similarity
      │
      ▼
Recognized / Unknown
      │
      ▼
Store Log
      │
      ▼
Dashboard Update
```

---

# 📊 Dashboard Features

## Statistics Cards

### Total Users

Displays total registered users

### Total Recognitions

Displays successful recognitions

### Unknown Faces

Displays unidentified faces

### Today's Activity

Daily recognition count

### Database Status

MongoDB Health

### Camera Status

Live Camera Connectivity

---

# 📈 Analytics Dashboard

### Pie Chart

Recognized vs Unknown

### Bar Chart

Daily Activity

### Line Chart

Weekly Recognition Trends

### Area Chart

Monthly Growth

### Live Metrics

Real-Time Statistics

---

# 📝 Recognition History

Features:

* Search
* Sort
* Pagination
* Date Filters
* CSV Export
* PDF Export

Columns:

| Name | Similarity | Status | Date | Time |
| ---- | ---------- | ------ | ---- | ---- |

---

# 👥 User Management

### Features

* View Users
* Edit Users
* Delete Users
* User Profile
* Face Image Preview
* Embedding Information

---

# ⚙️ Settings

### Recognition Threshold

Adjust similarity threshold dynamically

### Theme Control

Dark Mode Settings

### Database Monitoring

MongoDB Connection Status

### Camera Monitoring

Live Camera Health

---

# 🔌 API Endpoints

## Authentication

```http
POST /api/auth/login
```

## Face Registration

```http
POST /api/register-face
```

## Recognition

```http
POST /api/recognize
```

## Dashboard

```http
GET /api/dashboard
```

## Users

```http
GET /api/users

PUT /api/users/:id

DELETE /api/users/:id
```

## Logs

```http
GET /api/logs
```

## Analytics

```http
GET /api/analytics
```

## Settings

```http
GET /api/settings

PUT /api/settings
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/AI-Face-Recognition-System.git

cd AI-Face-Recognition-System
```

---

# Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

Run Backend

```bash
python app.py
```

Backend:

```bash
http://localhost:5000
```

---

# Frontend Setup

```bash
cd frontend

npm install
```

Run Frontend

```bash
npm run dev
```

Frontend:

```bash
http://localhost:5173
```

---

# MongoDB Setup

Install MongoDB

Create Database:

```bash
face_recognition_system
```

Connection:

```bash
mongodb://localhost:27017
```

---

# Performance

### Recognition Speed

* Less than 1 second

### Embedding Accuracy

* InsightFace Based

### Database

* Optimized Queries

### Dashboard

* Real-Time Updates

---

# Security Features

✔ JWT Authentication

✔ Password Hashing

✔ Protected APIs

✔ Input Validation

✔ Secure MongoDB Access

✔ Error Handling

✔ Logging

✔ Session Security

---

# Future Enhancements

* Multi-Camera Support
* Attendance Tracking
* Employee Monitoring
* Visitor Management
* Face Liveness Detection
* Email Notifications
* Cloud Deployment
* Docker Support
* Kubernetes Deployment

---

# 👨‍💻 Developed By

### Senior Full Stack AI Architecture

Built with:

❤️ React

❤️ Flask

❤️ MongoDB

❤️ InsightFace

❤️ OpenCV

---

<div align="center">

## ⭐ If you like this project, give it a star ⭐

### AI Face Recognition Management System

Enterprise AI Recognition Platform

</div>

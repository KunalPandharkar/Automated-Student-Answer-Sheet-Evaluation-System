# 📝 Subjective Analysis Project

Automate the grading of student answer sheets using Google Cloud Vision API for text extraction and NLP techniques for intelligent answer comparison.

![Subjective Analysis Banner](https://user-images.githubusercontent.com/your-username/banner-image.gif)

## 🚀 Features

✅ Automated answer sheet grading  
✅ Google Cloud Vision API for text extraction  
✅ NLP-based answer comparison  
✅ MySQL database for result storage  
✅ User-friendly web interface

---

## 📜 Table of Contents

- [📌 Prerequisites](#-prerequisites)
- [⚡ Setup Instructions](#-setup-instructions)
- [🛠 Technologies Used](#-technologies-used)
- [📄 License](#-license)
- [🙌 Contributing](#-contributing)
- [📞 Contact](#-contact)

---

## 📌 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.10.9** → [Download Here](https://www.python.org/downloads/release/python-3109/)
- **XAMPP (for MySQL database)** → [Download Here](https://www.apachefriends.org/index.html)
- **Google Cloud Vision API** → [Set up here](https://cloud.google.com/vision/docs/setup)

---

## ⚡ Setup Instructions

Follow these steps to set up the project:

### 1️⃣ Install Python 3.10.9
Download and install Python from the official website.

### 2️⃣ Install XAMPP & Start Services
Download XAMPP and start **Apache & MySQL** from the XAMPP Control Panel.

### 3️⃣ Create Database
Open `phpMyAdmin` and create a new database named:
```
subjective_analysis
```

### 4️⃣ Clone the Repository
Run the following command:
```bash
git clone https://github.com/KunalPandharkar/Subjective_Analysis.git
cd Subjective_Analysis
```

### 5️⃣ Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 6️⃣ Configure Environment Variables
Create a `.env` file in the project root and add:
```
GOOGLE_APPLICATION_CREDENTIALS=your-credentials.json
DATABASE_URL=mysql://root:@localhost/subjective_analysis
```

### 7️⃣ Run Migrations
```bash
python manage.py migrate
```

### 8️⃣ Start the Application
```bash
python manage.py runserver
```

🚀 Your project is now up and running!

---

## 🛠 Technologies Used

| Technology       | Purpose                      |
|-----------------|-----------------------------|
| Python 3.10.9   | Backend logic                |
| Django          | Web framework                |
| MySQL           | Database management          |
| Google Cloud Vision API | OCR for text extraction |
| Natural Language Processing (NLP) | Intelligent answer comparison |
| Bootstrap 5     | Frontend styling             |

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---

## 🙌 Contributing

💡 Contributions are welcome! Follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Added feature X'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a Pull Request

---

## 📞 Contact

💬 Have questions? Reach out to me:

📧 Email: [your-email@example.com](mailto:your-email@example.com)  
🐦 Twitter: [@your-handle](https://twitter.com/your-handle)  
📷 LinkedIn: [Your Profile](https://linkedin.com/in/your-profile)

---

⭐ **If you like this project, don't forget to give it a star!** ⭐

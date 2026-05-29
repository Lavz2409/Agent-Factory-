# 📦 Project Overview

The "Smart Health Risk Analyzer" is a full-stack web application built using the MERN stack (MongoDB, Express, React, Node.js). It allows users to upload their medical reports in PDF or image formats, extracts key health metrics using AI/ML models or APIs, analyzes the user's health risk level (Low, Medium, High), and provides personalized health recommendations. The application also includes user authentication, a clean dashboard UI, and stores user history for future reference.

**Key Features:**
- Upload and process medical reports in PDF/image format.
- Extract key health metrics like glucose, cholesterol, and TSH.
- Analyze and categorize health risk levels.
- Provide personalized health recommendations.
- User authentication and history management.
- Clean and intuitive dashboard UI.

# 🔄 Architecture & Execution Flow

1. **User Authentication**: Users sign up or log in to access the application.
2. **File Upload**: Users upload their medical reports via the frontend.
3. **File Processing**: The backend validates and processes the uploaded files.
4. **Data Extraction**: Key health metrics are extracted using AI/ML models.
5. **Risk Analysis**: The application analyzes the extracted data to determine the user's health risk level.
6. **Recommendations**: Personalized health recommendations are generated based on the analysis.
7. **Data Storage**: User data and history are stored in MongoDB.
8. **Dashboard Display**: The frontend retrieves and displays data on the dashboard.

```
+----------------+        +----------------+        +------------------+
|                |        |                |        |                  |
|   Frontend     |  --->  |   Backend      |  --->  |   Database       |
| (React)        |        | (Node/Express) |        |  (MongoDB)       |
|                |        |                |        |                  |
+----------------+        +----------------+        +------------------+
```

# 📁 Generated Files

| File                                   | Purpose                                      |
|----------------------------------------|----------------------------------------------|
| client/src/components/App.js           | Main React component for the application     |
| client/src/components/Dashboard.js     | Dashboard UI component                       |
| client/src/components/Login.js         | User login component                         |
| client/src/components/Signup.js        | User signup component                        |
| client/src/components/Upload.js        | File upload component                        |
| client/src/services/api.js             | Service for making API calls                 |
| server/app.js                          | Express application setup                    |
| server/routes/auth.js                  | Routes for authentication                    |
| server/routes/upload.js                | Routes for file upload and processing        |
| server/routes/user.js                  | Routes for user data management              |
| server/controllers/authController.js   | Controller for authentication logic          |
| server/controllers/uploadController.js | Controller for handling file uploads         |
| server/controllers/userController.js   | Controller for user data operations          |
| server/models/User.js                  | Mongoose model for user data                 |
| server/models/Report.js                | Mongoose model for medical reports           |
| server/middleware/authMiddleware.js    | Middleware for authentication checks         |
| server/utils/fileHandler.js            | Utility functions for file handling          |
| server/utils/aiAnalyzer.js             | Utility functions for AI/ML analysis         |
| server/config/db.js                    | Database connection setup                    |
| server/config/config.js                | Configuration for environment variables      |

# 📚 Libraries & Frameworks

| Library       | Type       | Purpose                                       | Install Command               |
|---------------|------------|-----------------------------------------------|-------------------------------|
| React         | Frontend   | Build user interfaces                         | `npx create-react-app`        |
| Express       | Backend    | Web framework for Node.js                     | `npm install express`         |
| Mongoose      | Backend    | MongoDB object modeling tool                  | `npm install mongoose`        |
| Axios         | Frontend   | Promise-based HTTP client for the browser     | `npm install axios`           |
| bcrypt        | Backend    | Password hashing                              | `npm install bcrypt`          |
| jsonwebtoken  | Backend    | JSON Web Token implementation                 | `npm install jsonwebtoken`    |
| dotenv        | Backend    | Loads environment variables from a .env file  | `npm install dotenv`          |
| multer        | Backend    | Middleware for handling multipart/form-data   | `npm install multer`          |
| cors          | Backend    | Middleware for enabling CORS                  | `npm install cors`            |

# ⚙️ Setup & Installation

1. **Python Version Requirement**: Ensure Python 3.8+ is installed for AI/ML integration.
2. **Install Backend Dependencies**:
    ```bash
    npm install express mongoose bcrypt jsonwebtoken dotenv multer cors
    ```
3. **Install Frontend Dependencies**:
    ```bash
    npm install axios
    ```
4. **Environment Configuration**: Create a `.env` file in the `server` directory with the following variables:
    ```
    PORT=5000
    MONGODB_URI=<your_mongodb_uri>
    JWT_SECRET=<your_jwt_secret>
    ```

# ▶️ Commands to Run

```bash
# Start the backend server
cd server
npm start

# Start the frontend development server
cd client
npm start
```

# 🧪 Test Cases

| #  | Input                               | Expected Output                                         | Pass Criteria                                   |
|----|-------------------------------------|---------------------------------------------------------|-------------------------------------------------|
| 1  | Valid login credentials             | User is redirected to the dashboard                     | Dashboard is displayed                          |
| 2  | Invalid login credentials           | Error message "Invalid email or password"               | Error message is shown                          |
| 3  | Valid file upload                   | Success message and analysis result displayed           | Analysis result is shown on the dashboard       |
| 4  | Invalid file format upload          | Error message "Invalid file format"                     | Error message is shown                          |
| 5  | Access dashboard without login      | Redirected to login page                                | Login page is displayed                         |

# 🔍 Manual Testing Steps

1. Navigate to the application URL in a web browser.
2. Click on the "Sign Up" link and create a new account.
3. Log in using the newly created account credentials.
4. Navigate to the "Upload" section and upload a valid medical report.
5. Verify that the analysis results and recommendations are displayed.
6. Check the "History" section to ensure the uploaded report is listed.

# 🚀 Future Improvements

- Implement a more advanced AI/ML model for better accuracy in health risk analysis.
- Add support for additional medical report formats.
- Integrate a notification system to alert users about critical health risks.
- Enhance the UI/UX for a more intuitive user experience.
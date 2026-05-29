# 📦 Project Overview

SpecTs is a full-stack e-commerce platform designed for purchasing spectacles, sunglasses, and lenses. It features a modern UI/UX with 3D product previews to enhance the shopping experience. The application includes a robust authentication system, a comprehensive product module, and a seamless checkout process. It also provides user and admin dashboards for managing orders and products.

### Key Features
- **Authentication System**: Secure user login and registration with JWT-based authentication and role-based access control.
- **Product Module**: Detailed product listings with categories, 3D previews, and comprehensive product information.
- **Advanced UI**: Modern, responsive design with interactive 3D product previews and smooth animations.
- **Cart & Checkout**: Efficient cart management and secure payment processing with Stripe or Razorpay.

# 🔄 Architecture & Execution Flow

1. **User Interaction**: Users interact with the frontend, triggering API calls to the backend.
2. **Authentication**: User credentials are verified, and JWT tokens are issued for session management.
3. **Product Retrieval**: The frontend requests product data, including 3D models, from the backend.
4. **Cart Management**: Users add products to their cart, which updates the global state.
5. **Checkout Process**: Users proceed to checkout, where payment details are processed via Stripe/Razorpay.
6. **Order Management**: Orders are stored in the database, and users can view their order history in the dashboard.
7. **Admin Operations**: Admins manage products and orders through the admin dashboard.

```
+------------+       +---------------+       +-------------+       +-------------+
|  Frontend  |<----->|  Backend API  |<----->|   Database  |<----->|  Payment API |
+------------+       +---------------+       +-------------+       +-------------+
```

# 📁 Generated Files

| File | Purpose |
|------|---------|
| /frontend/components/ProductCard.jsx | UI component for displaying product details. |
| /frontend/pages/index.js | Main landing page for the application. |
| /frontend/store/index.js | Global state management using Zustand. |
| /frontend/services/apiService.js | Utility functions for making API requests. |
| /frontend/3d/Product3DViewer.jsx | Component for rendering 3D product previews. |
| /backend/controllers/authController.js | Handles authentication-related API requests. |
| /backend/models/userModel.js | Mongoose schema for user data. |
| /backend/routes/auth.js | Defines authentication routes. |
| /backend/middleware/authenticate.js | Middleware for JWT authentication. |
| /backend/services/paymentService.js | Handles payment processing logic. |

# 📚 Libraries & Frameworks

| Library | Type | Purpose | Install Command |
|---------|------|---------|-----------------|
| React.js | Frontend | Building user interfaces | `npx create-react-app` |
| Next.js | Frontend | Server-side rendering | `npx create-next-app` |
| Tailwind CSS | Frontend | Styling and layout | `npm install tailwindcss` |
| Three.js | Frontend | 3D graphics rendering | `npm install three` |
| Zustand | Frontend | State management | `npm install zustand` |
| Node.js | Backend | Server environment | N/A |
| Express.js | Backend | Web framework for Node.js | `npm install express` |
| MongoDB | Database | Data storage | N/A |
| Mongoose | Backend | MongoDB ORM | `npm install mongoose` |
| JWT | Backend | Authentication | `npm install jsonwebtoken` |
| Stripe | Payment | Payment processing | `npm install stripe` |
| Cloudinary | Media | Image uploads | `npm install cloudinary` |

# ⚙️ Setup & Installation

1. **Python Version Requirement**: Ensure Python 3.x is installed for backend scripts.
2. **Install Dependencies**:
   ```bash
   # Frontend
   npm install react react-dom next tailwindcss three zustand
   # Backend
   npm install express mongoose jsonwebtoken stripe cloudinary
   ```
3. **Environment Configuration**: Create a `.env` file with the following variables:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
   MONGODB_URI=mongodb://localhost:27017/spects
   JWT_SECRET=your_jwt_secret
   STRIPE_SECRET_KEY=your_stripe_key
   CLOUDINARY_URL=your_cloudinary_url
   ```

# ▶️ Commands to Run

```bash
# Start the frontend
npm run dev

# Start the backend
node server.js
```

# 🧪 Test Cases

| # | Input | Expected Output | Pass Criteria |
|---|-------|-----------------|---------------|
| 1 | User login with valid credentials | JWT token | Token is returned |
| 2 | Fetch all products | Array of products | Products are listed |
| 3 | Add product to cart | Cart updated | Cart contains the product |
| 4 | Checkout with valid card | Payment success | Order is created |
| 5 | Admin adds new product | Product added | Product is retrievable |

# 🔍 Manual Testing Steps

1. **Register a New User**: Navigate to the signup page and create a new account.
2. **Login**: Use the newly created credentials to log in.
3. **Browse Products**: Navigate to the product listing page and view different categories.
4. **View 3D Product**: Select a product to view its 3D model and interact with it.
5. **Add to Cart**: Add a product to the cart and verify the cart updates.
6. **Checkout**: Proceed to checkout and complete a purchase using test payment details.

# 🚀 Future Improvements

- Implement social login using Firebase or Auth0 for a smoother authentication experience.
- Add a wishlist feature for users to save products for later.
- Enhance the search functionality with filters for price, brand, and gender.
- Integrate a reviews and ratings system for products to improve user engagement.
javascript
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Dashboard from './Dashboard';
import UploadReport from './UploadReport';
import Login from './Login';
import Signup from './Signup';
import Navbar from './Navbar';
import { AuthProvider } from '../context/AuthContext';
import PrivateRoute from './PrivateRoute';
import '../styles/App.css';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check for user authentication status on component mount
    const fetchUser = async () => {
      try {
        const response = await fetch('/api/auth/user');
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        }
      } catch (error) {
        console.error('Error fetching user:', error);
      }
    };

    fetchUser();
  }, []);

  return (
    <AuthProvider value={{ user, setUser }}>
      <Router>
        <div className="App">
          <Navbar />
          <Switch>
            <Route path="/login" component={Login} />
            <Route path="/signup" component={Signup} />
            <PrivateRoute path="/dashboard" component={Dashboard} />
            <PrivateRoute path="/upload" component={UploadReport} />
            <Route path="/" exact component={Login} />
          </Switch>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
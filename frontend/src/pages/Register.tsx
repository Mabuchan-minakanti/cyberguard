
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, User, Mail, Lock } from "lucide-react";
import "./Register.css";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPasswordError, setShowPasswordError] = useState(false);
  const passwordMismatch =
    confirmPassword.length > 0 && password !== confirmPassword;

  function handleRegister(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (password.length < 8 || passwordMismatch || password !== confirmPassword) {
      return;
    }

    alert("Registration form completed. Account creation will be connected to the backend next.");
    navigate("/login");
  }

  return (
    <main className="register-page">
      <Link to="/" className="register-brand">
        <ShieldCheck size={30} />
        <span>CyberGuard AI</span>
      </Link>

      <section className="register-card">
        <h1>Create your account</h1>
        <p>
          Join CyberGuard AI to analyze network traffic and investigate
          potential threats.
        </p>

        <form onSubmit={handleRegister}>
          <label htmlFor="name">Full name</label>
          <div className="register-input">
            <User size={18} />
            <input
              id="name"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <label htmlFor="register-email">Email address</label>
          <div className="register-input">
            <Mail size={18} />
            <input
              id="register-email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <label htmlFor="register-password">Password</label>
          <div className="register-input">
            <Lock size={18} />
            <input
              id="register-password"
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </div>

          <label htmlFor="confirm-password">Confirm password</label>
          <div className="register-input">
            <Lock size={18} />
            <input
              id="confirm-password"
              type="password"
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          {passwordMismatch && (
            <p className="password-error">
              Passwords do not match!
            </p>
          )}

          {confirmPassword.length > 0 && !passwordMismatch && (
            <p className="password-success">
              Passwords match!
            </p>
          )}

          <button
            type="submit"
            className="register-submit"
            disabled={passwordMismatch}
          >
            Create Account
          </button>
        </form>

        <div className="register-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </section>
    </main>
  );
}

export default Register;

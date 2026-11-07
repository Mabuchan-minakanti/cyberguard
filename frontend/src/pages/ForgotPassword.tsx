
import { useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Mail } from "lucide-react";
import "./ForgotPassword.css";

function ForgotPassword() {
  const [email, setEmail] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    alert("Password reset functionality will be connected to the backend.");
  }

  return (
    <main className="forgot-page">
      <Link to="/" className="forgot-brand">
        <ShieldCheck size={30} />
        CyberGraph
      </Link>

      <section className="forgot-card">
        <div className="forgot-icon">
          <Mail size={30} />
        </div>

        <h1>Forgot your password?</h1>
        <p>
          Enter your registered email address. We will use it to help
          you reset your password.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="forgot-email">Email address</label>

          <div className="forgot-input">
            <Mail size={18} />
            <input
              id="forgot-email"
              type="email"
              placeholder="Enter your registered email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button type="submit">Send Reset Instructions</button>
        </form>

        <Link to="/login" className="back-login">
          ← Back to Login
        </Link>
      </section>
    </main>
  );
}

export default ForgotPassword;


import { Link } from "react-router-dom";
import { Activity, ShieldCheck, Upload, Network } from "lucide-react";

function Dashboard() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#081426",
      color: "#f4f7fc",
      padding: "40px",
      fontFamily: "Arial, sans-serif"
    }}>
      <header style={{ marginBottom: "40px" }}>
        <Link to="/" style={{ color: "#60b5ff", textDecoration: "none" }}>
          ← Back to Home
        </Link>
        <h1 style={{ marginTop: "24px" }}>Security Dashboard</h1>
        <p style={{ color: "#aab8cc" }}>
          Welcome to your network threat monitoring workspace.
        </p>
      </header>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "20px"
      }}>
        {[
          { title: "Traffic Analysis", description: "Upload network traffic for analysis.", icon: Upload },
          { title: "Threat Detection", description: "Identify potentially suspicious connections.", icon: ShieldCheck },
          { title: "Graph Visualization", description: "Explore relationships between network devices.", icon: Network },
          { title: "System Activity", description: "View your analysis workspace.", icon: Activity }
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.title} style={{
              background: "#12233b",
              border: "1px solid #263b59",
              borderRadius: "14px",
              padding: "24px"
            }}>
              <Icon size={28} color="#60b5ff" />
              <h2>{item.title}</h2>
              <p style={{ color: "#aab8cc" }}>{item.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Dashboard;

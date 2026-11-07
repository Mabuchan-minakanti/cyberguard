
import { Link } from "react-router-dom";
import {
  ShieldCheck,
  Menu,
  ArrowRight,
  Network,
  BrainCircuit,
  Search,
  FileCheck,
  Upload,
  Activity,
  LockKeyhole,
  ChevronRight,
} from "lucide-react";
import "./Home.css";

const features = [
  {
    icon: Search,
    title: "Intelligent Threat Detection",
    description:
      "AI analyzes network connections to identify unusual and potentially harmful activity.",
  },
  {
    icon: Network,
    title: "Network Relationship Analysis",
    description:
      "Visualize how devices communicate and discover suspicious relationships across your network.",
  },
  {
    icon: BrainCircuit,
    title: "Understandable AI Results",
    description:
      "Discover why a connection was flagged instead of receiving an unexplained warning.",
  },
  {
    icon: FileCheck,
    title: "Security Reports",
    description:
      "Review your analysis and download reports to support further investigation.",
  },
];

function Home() {
  return (
    <div className="home-page">
      <header className="home-navbar">
        <Link to="/" className="home-brand">
          <span className="brand-icon">
            <ShieldCheck size={25} />
          </span>
          <span>CyberGraph</span>
        </Link>

        <nav className="home-nav-links">
          <a href="#home">Home</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#features">Features</a>
          <a href="#about">About</a>
        </nav>

        <div className="home-nav-actions">
          <Link to="/login" className="login-link">Log in</Link>
          <Link to="/register" className="nav-cta">
            Get Started <ArrowRight size={16} />
          </Link>
        </div>

        <button className="mobile-menu" aria-label="Menu">
          <Menu size={23} />
        </button>
      </header>

      <main>
        <section className="hero-section" id="home">
          <div className="hero-content">
            <div className="hero-label">
              <span className="hero-label-dot" />
              AI-POWERED NETWORK SECURITY
            </div>

            <h1>
              Your Network.
              <br />
              <span>Protected by Intelligence.</span>
            </h1>

            <p className="hero-description">
              Understand what's happening across your network.
              Detect suspicious connections with AI and discover
              why they may be dangerous — all in one platform.
            </p>

            <div className="hero-buttons">
              <Link to="/register" className="primary-cta">
                Get Started <ArrowRight size={18} />
              </Link>
              <a href="#how-it-works" className="secondary-cta">
                Discover How It Works
              </a>
            </div>

            <div className="hero-trust">
              <span><ShieldCheck size={16} /> AI-assisted detection</span>
              <span><BrainCircuit size={16} /> Explainable results</span>
            </div>
          </div>

          <div className="hero-visual">
            <div className="visual-glow" />
            <div className="visual-card">
              <div className="visual-card-top">
                <div>
                  <span className="visual-eyebrow">NETWORK INTELLIGENCE</span>
                  <h3>Security overview</h3>
                </div>
                <span className="visual-live">
                  <i /> AI ANALYSIS
                </span>
              </div>

              <div className="network-art">
                <div className="network-ring ring-one" />
                <div className="network-ring ring-two" />
                <div className="network-line line-one" />
                <div className="network-line line-two" />
                <div className="network-line line-three" />
                <div className="network-line line-four" />

                <div className="network-node node-center">
                  <ShieldCheck size={31} />
                </div>
                <div className="network-node node-one"><Activity size={17} /></div>
                <div className="network-node node-two"><Network size={17} /></div>
                <div className="network-node node-three"><LockKeyhole size={17} /></div>
                <div className="network-node node-four"><Activity size={17} /></div>
              </div>

              <div className="visual-bottom">
                <div>
                  <span className="visual-eyebrow">DETECTION APPROACH</span>
                  <strong>Graph Neural Network</strong>
                </div>
                <span className="visual-chip">GraphSAGE</span>
              </div>
            </div>

            <div className="floating-note note-top">
              <span className="note-icon"><BrainCircuit size={17} /></span>
              <span><strong>Explainable AI</strong><small>Understand every alert</small></span>
            </div>

            <div className="floating-note note-bottom">
              <span className="note-icon green"><ShieldCheck size={17} /></span>
              <span><strong>Smarter monitoring</strong><small>Connection-based analysis</small></span>
            </div>
          </div>
        </section>

        <section className="intro-strip">
          <p>
            CyberGraph turns complex network activity into security insights
            that are easier to understand.
          </p>
        </section>

        <section className="section-block how-section" id="how-it-works">
          <div className="section-heading">
            <span className="section-kicker">HOW IT WORKS</span>
            <h2>Network security, made simple.</h2>
            <p>
              You don't need to be a cybersecurity expert to understand
              the analysis. Follow four simple steps.
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <span className="step-number">01</span>
              <div className="step-icon"><Upload size={23} /></div>
              <h3>Upload Traffic</h3>
              <p>Provide a supported network traffic CSV file for analysis.</p>
              <span className="step-arrow"><ChevronRight size={20} /></span>
            </div>

            <div className="step-card">
              <span className="step-number">02</span>
              <div className="step-icon"><BrainCircuit size={23} /></div>
              <h3>AI Analysis</h3>
              <p>Our GraphSAGE model examines relationships between network connections.</p>
              <span className="step-arrow"><ChevronRight size={20} /></span>
            </div>

            <div className="step-card">
              <span className="step-number">03</span>
              <div className="step-icon"><ShieldCheck size={23} /></div>
              <h3>Detect Threats</h3>
              <p>Identify connections that the model classifies as potentially suspicious.</p>
              <span className="step-arrow"><ChevronRight size={20} /></span>
            </div>

            <div className="step-card">
              <span className="step-number">04</span>
              <div className="step-icon"><FileCheck size={23} /></div>
              <h3>Understand Results</h3>
              <p>Explore risk scores, explanations and reports for further investigation.</p>
            </div>
          </div>
        </section>

        <section className="section-block features-section" id="features">
          <div className="section-heading">
            <span className="section-kicker">WHAT CYBERGRAPH OFFERS</span>
            <h2>More than just threat alerts.</h2>
            <p>
              Get meaningful insights into your network instead of
              confusing technical warnings.
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <article className="feature-card" key={feature.title}>
                  <div className="feature-icon"><Icon size={23} /></div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section className="section-block about-section" id="about">
          <div className="about-copy">
            <span className="section-kicker">ABOUT THE PROJECT</span>
            <h2>Making AI security easier to understand.</h2>
            <p>
              CyberGraph is an AI-assisted network threat detection platform
              built around Graph Neural Networks. Instead of looking at each
              network flow in isolation, it analyzes relationships between
              communicating devices.
            </p>
            <p>
              Its explainable AI approach aims to help users understand
              why a connection received a suspicious classification,
              supporting informed security investigation.
            </p>
            <Link to="/register" className="text-cta">
              Explore CyberGraph <ArrowRight size={17} />
            </Link>
          </div>

          <div className="about-visual">
            <div className="about-icon"><Network size={48} /></div>
            <h3>Graph Neural Networks</h3>
            <p>
              Analyze connections and relationships, not just isolated records.
            </p>
            <div className="technology-tags">
              <span>GraphSAGE</span>
              <span>Explainable AI</span>
              <span>FastAPI</span>
              <span>React</span>
            </div>
          </div>
        </section>

        <section className="final-cta">
          <div className="cta-shield"><ShieldCheck size={34} /></div>
          <span className="section-kicker">TAKE THE FIRST STEP</span>
          <h2>Make your network activity easier to understand.</h2>
          <p>Start exploring AI-assisted network threat analysis with CyberGraph.</p>
          <Link to="/register" className="primary-cta">
            Get Started <ArrowRight size={18} />
          </Link>
        </section>
      </main>

      <footer className="home-footer">
        <Link to="/" className="home-brand">
          <span className="brand-icon"><ShieldCheck size={21} /></span>
          <span>CyberGraph</span>
        </Link>
        <p>AI-assisted network threat detection with explainable insights.</p>
        <span>© 2026 CyberGraph · Academic Project</span>
      </footer>
    </div>
  );
}

export default Home;

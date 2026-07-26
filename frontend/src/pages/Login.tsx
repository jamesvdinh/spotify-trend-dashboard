import { loginUrl } from "../api";

export default function Login() {
  return (
    <div className="page">
      <div className="login-card">
        <div className="logo-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none">
            <path d="M4 15c4.5-2 11-2 15.5 0" stroke="#000" strokeWidth="2" strokeLinecap="round" />
            <path d="M3.5 11c5.5-2.4 11.5-2.4 17 0" stroke="#000" strokeWidth="2" strokeLinecap="round" />
            <path d="M3 7c6.5-2.8 11.5-2.8 18 0" stroke="#000" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
        <h1>Spotify Trend Dashboard</h1>
        <p>
          Connect your Spotify account to see how your listening habits stack up
          against global charts and rising artists.
        </p>
        <a className="btn-spotify" href={loginUrl()}>
          Connect with Spotify
        </a>
      </div>
    </div>
  );
}

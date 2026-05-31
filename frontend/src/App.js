import { useState } from "react";
import ReactMarkdown from "react-markdown";

// const API = "http://34.207.244.92:10000";
const API = "http://127.0.0.1:8001";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState("openrouter");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input, provider }),
      });
      const data = await res.json();
      const reply = data?.choices?.[0]?.message?.content || data?.response || "No response";
      setMessages(prev => [...prev, { role: "ai", text: reply }]);
    } catch {
      setMessages(prev => [...prev, { role: "ai", text: "Error reaching backend." }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>AI Automation Chat</h2>
      <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, minHeight: 400, marginBottom: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.role === "user" ? "right" : "left", margin: "8px 0" }}>
            <div
              style={{
                background: m.role === "user" ? "#185FA5" : "#f0f0f0",
                color: m.role === "user" ? "#fff" : "#000",
                padding: "8px 14px",
                borderRadius: 12,
                display: "inline-block",
                maxWidth: "75%",
                textAlign: "left",
              }}
            >
              {m.role === "user" ? (
                m.text
              ) : (
                <ReactMarkdown
                  components={{
                    code({ inline, children, ...props }) {
                      return inline ? (
                        <code
                          style={{
                            background: "#e0e0e0",
                            borderRadius: 4,
                            padding: "1px 5px",
                            fontFamily: "monospace",
                            fontSize: 13,
                          }}
                          {...props}
                        >
                          {children}
                        </code>
                      ) : (
                        <pre
                          style={{
                            background: "#1e1e1e",
                            color: "#f8f8f2",
                            borderRadius: 8,
                            padding: "12px 16px",
                            overflowX: "auto",
                            fontSize: 13,
                            fontFamily: "monospace",
                            margin: "8px 0",
                          }}
                        >
                          <code {...props}>{children}</code>
                        </pre>
                      );
                    },
                    p({ children }) {
                      return <p style={{ margin: "4px 0" }}>{children}</p>;
                    },
                    h1({ children }) {
                      return <h1 style={{ fontSize: 18, margin: "8px 0 4px" }}>{children}</h1>;
                    },
                    h2({ children }) {
                      return <h2 style={{ fontSize: 16, margin: "8px 0 4px" }}>{children}</h2>;
                    },
                    h3({ children }) {
                      return <h3 style={{ fontSize: 14, margin: "6px 0 4px" }}>{children}</h3>;
                    },
                    ul({ children }) {
                      return <ul style={{ paddingLeft: 20, margin: "4px 0" }}>{children}</ul>;
                    },
                    ol({ children }) {
                      return <ol style={{ paddingLeft: 20, margin: "4px 0" }}>{children}</ol>;
                    },
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        {loading && <p style={{ color: "#999" }}>Thinking...</p>}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <select
          value={provider}
          onChange={e => setProvider(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: 6, border: "1px solid #ddd" }}
        >
          <option value="openrouter">OpenRouter</option>
          <option value="openai">OpenAI</option>
        </select>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Type a message..."
          style={{ flex: 1, padding: "8px 12px", borderRadius: 6, border: "1px solid #ddd" }}
        />
        <button
          onClick={send}
          style={{ padding: "8px 16px", borderRadius: 6, background: "#185FA5", color: "#fff", border: "none", cursor: "pointer" }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

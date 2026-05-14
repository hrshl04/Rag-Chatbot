import React, { useState, useRef, useEffect } from "react";

function App() {

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages]);

  // Ask Question
  const askQuestion = async () => {

    if (!question.trim()) return;

    const updatedMessages = [
      ...messages,
      {
        sender: "user",
        text: question
      }
    ];

    setMessages(updatedMessages);
    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            question: question
          })
        }
      );

      const data = await response.json();

      setMessages([
        ...updatedMessages,
        {
          sender: "ai",
          text: data.answer,
          sources: data.sources || []
        }
      ]);

    } catch (error) {

      setMessages([
        ...updatedMessages,
        {
          sender: "ai",
          text: "Error connecting to backend."
        }
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  // Upload PDF
  const uploadFile = async (event) => {

    const file = event.target.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {

      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        {
          sender: "ai",
          text: data.message || "File uploaded successfully."
        }
      ]);

    } catch (error) {

      setMessages(prev => [
        ...prev,
        {
          sender: "ai",
          text: "File upload failed."
        }
      ]);
    }

    setLoading(false);
  };

  // Enter key support
  const handleKeyDown = (e) => {

    if (e.key === "Enter") {
      askQuestion();
    }
  };

  return (

    <div style={{
      backgroundColor: "#020617",
      minHeight: "100vh",
      color: "white",
      fontFamily: "Arial",
      padding: "20px"
    }}>

      <div style={{
        maxWidth: "950px",
        margin: "0 auto"
      }}>

        {/* HEADER */}

        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px"
        }}>

          <h1>
            🤖 AI RAG Chatbot
          </h1>

          {/* Upload Button */}

          <button
            onClick={() => fileInputRef.current.click()}
            style={{
              backgroundColor: "#1d4ed8",
              color: "white",
              border: "none",
              padding: "12px 18px",
              borderRadius: "10px",
              cursor: "pointer",
              fontSize: "14px"
            }}
          >
            Upload PDF
          </button>

          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={uploadFile}
          />

        </div>

        {/* CHAT AREA */}

        <div style={{
          backgroundColor: "#0f172a",
          borderRadius: "16px",
          padding: "20px",
          height: "70vh",
          overflowY: "auto",
          border: "1px solid #1e293b"
        }}>

          {messages.length === 0 && (

            <div style={{
              color: "#94a3b8",
              textAlign: "center",
              marginTop: "100px"
            }}>
              Ask something or upload a PDF...
            </div>

          )}

          {messages.map((msg, index) => (

            <div
              key={index}
              style={{
                display: "flex",
                justifyContent:
                  msg.sender === "user"
                    ? "flex-end"
                    : "flex-start",
                marginBottom: "18px"
              }}
            >

              <div style={{
                maxWidth: "75%",
                padding: "15px",
                borderRadius: "16px",
                backgroundColor:
                  msg.sender === "user"
                    ? "#2563eb"
                    : "#1e293b",
                lineHeight: "1.6"
              }}>

                <strong>
                  {msg.sender === "user"
                    ? "You"
                    : "AI"}
                </strong>

                <div style={{
                  marginTop: "8px",
                  whiteSpace: "pre-wrap"
                }}>
                  {msg.text}
                </div>

                {/* Sources */}

                {msg.sources &&
                  msg.sources.length > 0 && (

                  <div style={{
                    marginTop: "12px",
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "8px"
                  }}>

                    {msg.sources.map((src, i) => (

                      <span
                        key={i}
                        style={{
                          backgroundColor: "#334155",
                          padding: "5px 10px",
                          borderRadius: "999px",
                          fontSize: "12px",
                          color: "#cbd5e1"
                        }}
                      >
                        📄 {src}
                      </span>

                    ))}

                  </div>

                )}

              </div>

            </div>

          ))}

          {/* Loading */}

          {loading && (

            <div style={{
              color: "#94a3b8",
              marginTop: "10px"
            }}>
              AI is thinking...
            </div>

          )}

          <div ref={chatEndRef} />

        </div>

        {/* INPUT AREA */}

        <div style={{
          display: "flex",
          gap: "10px",
          marginTop: "20px"
        }}>

          <input
            type="text"
            placeholder="Ask something..."
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            onKeyDown={handleKeyDown}
            style={{
              flex: 1,
              padding: "16px",
              borderRadius: "12px",
              border: "1px solid #334155",
              backgroundColor: "#0f172a",
              color: "white",
              fontSize: "15px",
              outline: "none"
            }}
          />

          <button
            onClick={askQuestion}
            style={{
              padding: "16px 24px",
              backgroundColor: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "12px",
              cursor: "pointer",
              fontSize: "15px",
              fontWeight: "bold"
            }}
          >
            Send
          </button>

        </div>

      </div>

    </div>
  );
}

export default App;
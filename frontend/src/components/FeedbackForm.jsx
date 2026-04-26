import React, { useState } from "react";
import { submitFeedback } from "../services/feedback";
import { useAuth } from "../context/AuthContext";

const FeedbackForm = () => {
  const { token } = useAuth();
  const [message, setMessage] = useState("");
  const [msg, setMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await submitFeedback(message, token);
    setMsg(res.data.msg);
    setMessage("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea value={message} onChange={e => setMessage(e.target.value)} required />
      <button type="submit">Send Feedback</button>
      {msg && <div>{msg}</div>}
    </form>
  );
};

export default FeedbackForm;
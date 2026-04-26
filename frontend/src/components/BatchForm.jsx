import React, { useState } from "react";
import { createBatch } from "../services/batch";
import { useAuth } from "../context/AuthContext";

const BatchForm = () => {
  const { token } = useAuth();
  const [batchCode, setBatchCode] = useState("");
  const [msg, setMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await createBatch(batchCode, token);
    setMsg(res.data.msg);
    setBatchCode("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={batchCode} onChange={e => setBatchCode(e.target.value)} required />
      <button type="submit">Create Batch</button>
      {msg && <div>{msg}</div>}
    </form>
  );
};

export default BatchForm;
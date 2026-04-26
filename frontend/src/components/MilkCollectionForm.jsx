import React, { useState } from "react";
import { collectMilk } from "../services/api";

const MilkCollectionForm = ({ farmerId, token, onSuccess }) => {
  const [quantity, setQuantity] = useState("");
  const [fat, setFat] = useState("");
  const [snf, setSnf] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await collectMilk(
        {
          farmer_id: farmerId,
          quantity_liters: parseFloat(quantity),
          fat_percentage: fat ? parseFloat(fat) : undefined,
          snf_percentage: snf ? parseFloat(snf) : undefined,
          notes: notes || undefined,
        },
        token
      );
      setQuantity("");
      setFat("");
      setSnf("");
      setNotes("");
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to record milk collection. Please try again."
      );
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md p-4 bg-white rounded shadow">
      <h2 className="text-lg font-bold mb-2">Milk Collection</h2>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <div className="mb-2">
        <label className="block">Quantity (liters):</label>
        <input
          type="number"
          step="0.01"
          min="0"
          required
          value={quantity}
          onChange={e => setQuantity(e.target.value)}
          className="border rounded px-2 py-1 w-full"
        />
      </div>
      <div className="mb-2">
        <label className="block">Fat %:</label>
        <input
          type="number"
          step="0.01"
          min="0"
          max="100"
          value={fat}
          onChange={e => setFat(e.target.value)}
          className="border rounded px-2 py-1 w-full"
        />
      </div>
      <div className="mb-2">
        <label className="block">SNF %:</label>
        <input
          type="number"
          step="0.01"
          min="0"
          max="100"
          value={snf}
          onChange={e => setSnf(e.target.value)}
          className="border rounded px-2 py-1 w-full"
        />
      </div>
      <div className="mb-2">
        <label className="block">Notes:</label>
        <textarea
          value={notes}
          onChange={e => setNotes(e.target.value)}
          className="border rounded px-2 py-1 w-full"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Saving..." : "Collect Milk"}
      </button>
    </form>
  );
};

export default MilkCollectionForm;
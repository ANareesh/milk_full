import React, { useEffect, useState } from "react";
import { fetchCollectionSummary, fetchPerformanceAnalytics, fetchPaymentTrends } from "../../services/analytics";
import { useAuth } from "../../context/AuthContext";

const AnalyticsPage = () => {
  const { token } = useAuth();
  const [summary, setSummary] = useState({});
  const [performance, setPerformance] = useState({});
  const [payments, setPayments] = useState({});

  useEffect(() => {
    fetchCollectionSummary("monthly", token).then(res => setSummary(res.data));
    fetchPerformanceAnalytics(token).then(res => setPerformance(res.data));
    fetchPaymentTrends(token).then(res => setPayments(res.data));
  }, [token]);

  return (
    <div>
      <h2>Analytics & Reporting</h2>
      <div>Monthly Collected: {summary.total_collected}</div>
      <div>Average Fat: {performance.avg_fat}</div>
      <div>Total Collections: {performance.collections}</div>
      <div>Total Payments: {payments.total_payments}</div>
    </div>
  );
};

export default AnalyticsPage;
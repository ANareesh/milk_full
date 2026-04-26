import axios from "axios";

export const fetchCollectionSummary = (period, token) =>
  axios.get(`/api/v1/analytics/summary?period=${period}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const fetchPerformanceAnalytics = (token) =>
  axios.get("/api/v1/analytics/performance", {
    headers: { Authorization: `Bearer ${token}` },
  });

export const fetchPaymentTrends = (token) =>
  axios.get("/api/v1/analytics/payment-trends", {
    headers: { Authorization: `Bearer ${token}` },
  });
import { apiClient } from "./api";
import { Invoice } from "../types";

export const invoiceService = {
  async listForCustomer(customerId: number): Promise<Invoice[]> {
    const response = await apiClient.get<{ data: Invoice[] }>(
      `/customers/${customerId}/invoices`
    );
    return response.data.data;
  },

  async getInvoice(invoiceId: number): Promise<Invoice> {
    const response = await apiClient.get<Invoice>(`/invoices/${invoiceId}`);
    return response.data;
  }
};
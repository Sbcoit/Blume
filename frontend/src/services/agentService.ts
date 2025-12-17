/**
 * Agent service for managing agent configuration and phone number registration
 */

export interface RegisterPhoneRequest {
  agentName: string;
  phone: string; // E.164 format (e.g., +15551234567)
}

export interface RegisterPhoneResponse {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Register a phone number and trigger a confirmation message from the agent
 */
export async function registerPhoneNumber(
  data: RegisterPhoneRequest
): Promise<RegisterPhoneResponse> {
  // TODO: Replace with real backend call once API is available
  // const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/agent/connect`, {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  //   body: JSON.stringify(data),
  // });
  // if (!res.ok) {
  //   const error = await res.json();
  //   throw new Error(error.message || "Failed to register phone number");
  // }
  // return res.json();

  // For now, simulate the API call
  console.log("[agentService] Register phone number", data);
  
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500));
  
  // Simulate success response
  return {
    success: true,
    message: `Confirmation message sent to ${data.phone}`,
  };
}

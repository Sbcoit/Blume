import { WorkflowExecution } from "@/types/workflow";
import { mockExecutions } from "@/lib/mockData";
// import { getSupabaseClient } from "@/services/supabaseClient";

export async function getWorkflowExecutions(): Promise<WorkflowExecution[]> {
  // Example REST call (replace mock once backend is live):
  // const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows`, {
  //   cache: "no-store"
  // });
  // if (!res.ok) throw new Error("Failed to fetch workflows");
  // return res.json();

  return mockExecutions;
}

export async function getWorkflowExecutionById(
  id: string
): Promise<WorkflowExecution | null> {
  // Example Supabase pattern:
  // const supabase = getSupabaseClient();
  // const { data, error } = await supabase
  //   .from("workflow_executions")
  //   .select("*")
  //   .eq("id", id)
  //   .single();
  // if (error) throw error;
  // return transformRowToExecution(data);

  return mockExecutions.find((e) => e.id === id) ?? null;
}

export async function confirmWorkflowStep(
  executionId: string,
  stepId: string
): Promise<void> {
  // Example: call backend to mark a step as approved.
  // await fetch(
  //   `${process.env.NEXT_PUBLIC_API_URL}/workflows/${executionId}/steps/${stepId}/confirm`,
  //   { method: "POST" }
  // );
  console.log("[workflowService] Confirm step", { executionId, stepId });
}



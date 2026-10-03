# Erratum to PREREGISTRATION_framing_ablation_v2.md

*3 October 2026. The pre-registration itself is unchanged.*

The v2 pre-registration states that Arm A's round 1 trained at batch size 8. That statement is not supported by the run records.

Arm A's first two attempts ran at batch size 8 and failed on memory before completing a round. The configuration was changed to batch size 4 at 15:52 on 30 September 2026, and round 1's adapter was saved at 16:42, which indicates that it trained at batch size 4. Round 2 trained for 819 steps, consistent with batch size 4. Round 1's batch size is not otherwise recorded.

The uncontrolled difference the sentence described therefore did not affect any completed round of that arm. The second-seed replication (Arm A2 against Arm B2) was run for the other reasons the pre-registration gives and is unaffected.

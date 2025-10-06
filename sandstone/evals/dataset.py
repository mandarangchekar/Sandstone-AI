"""Dataset with 8 gold-standard benchmark cases for NDA redlining evaluation."""

from typing import Any

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import IsInstance, LLMJudge

from sandstone.models.redline import RedlineIssue
from sandstone.evals.evaluators import SemanticSimilarity
from sandstone.evals.models import TaskInputs


# Define the 8 gold-standard benchmark cases
redlining_dataset = Dataset[TaskInputs, RedlineIssue, Any](
    name="nda_redlining_benchmark",
    cases=[
        Case(
            name="confidential_information",
            inputs=TaskInputs(
                expected_clause_type="Confidential Information"
            ),
            expected_output={
                "text_snippet": "\"Confidential Information\" shall mean any and all data, materials, documents, specifications, designs, drawings, models, samples, reports, analyses, or any other information furnished by Discloser, whether in written, electronic, graphic, oral, or any other form, but only to the extent that such information is labeled or otherwise identified in writing by Discloser as \"Confidential\" at the time of disclosure.",
                "playbook_clause_reference": "Confidential Information",
                "suggested_fix": "\"Confidential Information\" means all information of a confidential nature owned or used by, or relating to Discloser regardless of form (oral, written or electronic), whether identified or designated as confidential or proprietary, or not, or that, due to the nature of such information or under the circumstances surrounding its disclosure reasonably should be understood to be treated as confidential by Recipient, whether disclosed before, on or after the date of signature;"
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should address the same legal requirements as the expected fix (broadening definition to include all confidential info, not just labeled)"
                ),
            ],
        ),
        Case(
            name="recipients_obligations",
            inputs=TaskInputs(
                expected_clause_type="Recipient's Obligations"
            ),
            expected_output={
                "text_snippet": "Recipient may use Confidential Information solely for its own internal business purposes, including, without limitation, evaluation, analysis, or discussion concerning a potential business relationship or transaction with Discloser.",
                "playbook_clause_reference": "Recipient's Obligations",
                "suggested_fix": "1. Keep confidential. Recipient will keep the Confidential Information confidential and will take all reasonable and appropriate security precautions to maintain the confidentiality of the Confidential Information (which will include applying the same degree of care and security precautions as it takes to protect Recipient's own confidential information);\n2. Only use for permitted purpose. Recipient will only use the Confidential Information for the specific purpose set out in this Agreement;\n3. Limit internal access. Recipient will only disclose the Confidential Information to its personnel, contractors, or advisors who have a need to know and who are bound by confidentiality obligations no less protective than those set out in this Agreement;\n4. No reverse engineering. Recipient will not reverse engineer, decompile, or disassemble any software or materials comprising part of the Confidential Information;\n5. Notify breaches. Recipient will promptly notify Discloser of any unauthorized loss, disclosure, breach, or misuse of the Confidential Information;\n6. Standard exceptions. The obligations above will not apply to information that is already known without obligation of confidence, publicly available (other than through breach), independently developed, or disclosed with Discloser's prior written consent."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should provide comprehensive obligations including confidentiality, limited use, access control, breach notification, and standard exceptions"
                ),
            ],
        ),
        Case(
            name="return_of_confidential_information",
            inputs=TaskInputs(
                expected_clause_type="Return of confidential information"
            ),
            expected_output={
                "text_snippet": "Upon written request of Discloser or upon termination of this Agreement, Recipient may, at its sole discretion, either return to Discloser or destroy all physical and electronic embodiments of Confidential Information.",
                "playbook_clause_reference": "Return of confidential information",
                "suggested_fix": "On receipt of a written request from Discloser, Recipient will:\n- return to Discloser all documentation and materials (including any originals, copies, reproductions or summaries) containing Discloser's Confidential Information; or\n- at Discloser's option, destroy such documentation and materials;\nRecipient will certify in writing as soon as possible after the return or destruction that it has complied with these requirements."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should make return/destruction mandatory (not optional) and require written certification"
                ),
            ],
        ),
        Case(
            name="disclosure_required_by_law",
            inputs=TaskInputs(
                expected_clause_type="Disclosure required by Law"
            ),
            expected_output={
                "text_snippet": "If Recipient or any of its Representatives is required by applicable law, regulation, or judicial or governmental order to disclose any Confidential Information, Recipient may do so without prior notice to Discloser and without seeking to limit the scope of such disclosure.",
                "playbook_clause_reference": "Disclosure required by Law",
                "suggested_fix": "Recipient may disclose Confidential Information if required by law or by a valid order of a court or governmental authority, provided that, to the extent permitted by law, Recipient:\n- gives Discloser reasonable prior written notice of the required disclosure;\n- consults with Discloser on steps to limit disclosure;\n- uses reasonable endeavours to obtain assurance that the disclosed information will remain confidential."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should require prior notice, consultation, and efforts to limit disclosure"
                ),
            ],
        ),
        Case(
            name="indemnity",
            inputs=TaskInputs(
                expected_clause_type="Indemnity"
            ),
            expected_output={
                "text_snippet": "Neither Party shall have any liability to the other for any unauthorized disclosure, use, or loss of Confidential Information. Recipient shall not be liable for any breach of confidentiality, and Discloser waives any claims for damages or injunctive relief.",
                "playbook_clause_reference": "Indemnity",
                "suggested_fix": "Recipient agrees to indemnify, defend and hold Discloser (and Discloser's personnel) harmless against any and all loss, damage (including attorneys' fees on an attorney and own client basis), costs and expenses that Discloser may suffer or incur arising directly or indirectly from:\n- any unauthorized disclosure or use of Confidential Information by Recipient or its personnel;\n- any breach of this Agreement by Recipient or its personnel;\n- any willful misconduct or fraud by Recipient or its personnel."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should reverse the liability waiver and establish Recipient's indemnity obligations"
                ),
            ],
        ),
        Case(
            name="assignment",
            inputs=TaskInputs(
                expected_clause_type="Assignment"
            ),
            expected_output={
                "text_snippet": "Recipient may freely assign, transfer, or delegate its rights and obligations under this Agreement, in whole or in part, to any affiliate, successor, or acquirer, without the need for any consent or notice to Discloser.",
                "playbook_clause_reference": "Assignment",
                "suggested_fix": "No party may assign its rights or delegate its obligations under this Agreement, in whole or in part, without the prior written consent of the other party. However, Discloser may assign this Agreement, without consent, to any successor or purchaser of its business or substantially all of its assets."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should prohibit free assignment and require written consent"
                ),
            ],
        ),
        Case(
            name="notices_and_domicile",
            inputs=TaskInputs(
                expected_clause_type="Notices and domicile"
            ),
            expected_output={
                "text_snippet": "Email shall suffice as notice notwithstanding any failure of the intended recipient to receive such email.",
                "playbook_clause_reference": "Notices and domicile",
                "suggested_fix": "Notices. All notices under this Agreement must be in writing and delivered by hand, prepaid registered post, courier, or email to the addresses set out in this Agreement. A notice is deemed delivered on the date of hand delivery, three days after posting, the date of courier receipt confirmation, or the date of email transmission (provided no delivery failure notification is received)."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should define proper notice delivery methods and confirmation requirements"
                ),
            ],
        ),
        Case(
            name="general",
            inputs=TaskInputs(
                expected_clause_type="General"
            ),
            expected_output={
                "text_snippet": "The Parties agree that any oral agreements, understandings, or representations shall be legally binding, and no written amendment or signature shall be necessary to effectuate any modification to this Agreement.",
                "playbook_clause_reference": "General",
                "suggested_fix": "Entire Agreement. This Agreement constitutes the entire agreement between the parties on its subject matter and supersedes all prior discussions, understandings, and agreements, whether written or oral. No amendment or variation of this Agreement is effective unless in writing and signed by authorised representatives of both parties."
            },
            evaluators=[
                SemanticSimilarity(threshold=0.75),
                LLMJudge(
                    rubric="Generated fix should require written amendments with signatures"
                ),
            ],
        ),
    ],
    evaluators=[
        IsInstance(type_name="RedlineIssue"),
        LLMJudge(
            rubric=(
                "Output must have a valid playbook_clause_reference that matches "
                "one of these 8 expected clause types: 'Confidential Information', "
                "'Recipient's Obligations', 'Return of confidential information', "
                "'Disclosure required by Law', 'Indemnity', 'Assignment', "
                "'Notices and domicile', 'General'"
            ),
            include_input=False,
        ),
    ],
)

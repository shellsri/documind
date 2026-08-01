"""
Generates a couple of realistic sample PDFs (intern handbook, requisition
policy) so the RAG pipeline has something to index and demo immediately,
without needing you to source real documents first.

Run:  python sample_docs/generate_samples.py
"""

import os
import textwrap
from fpdf import FPDF


OUT_DIR = os.path.dirname(os.path.abspath(__file__))

DOCS = {
    "intern_handbook.pdf": (
        "Intern Handbook",
        """
        Section 1: Working Hours
        Interns are expected to work from 9:30 AM to 5:30 PM, Monday through Saturday.
        Punctuality is mandatory and repeated late arrivals may affect the final evaluation.

        Section 2: Leave Policy
        Interns are entitled to two days of casual leave per month. Leave requests must be
        submitted at least 48 hours in advance through the reporting supervisor, except in
        cases of medical emergency. Unapproved absences will be deducted from the attendance
        percentage used to calculate the final stipend.

        Section 3: Attendance and Stipend
        A minimum of 75 percent attendance is required for stipend eligibility. Attendance is
        tracked daily and reviewed at the midpoint and end of the internship.

        Section 4: Code of Conduct
        Interns must maintain confidentiality of all data and systems they are exposed to
        during the internship. Personal smartphones and laptops are not permitted inside
        secure office premises; devices may be deposited at the security desk upon entry.

        Section 5: Documentation Requirements
        All interns must submit a degree verification certificate, a police verification
        certificate, a government-issued ID, and recent passport-size photographs on the
        first day of joining. Incomplete documentation may lead to delayed onboarding.
        """,
    ),
    "requisition_policy.pdf": (
        "Equipment Requisition Policy",
        """
        Section 1: Purpose
        This document defines the process for requesting equipment and supplies across
        departments, including Logistics, Signals, Engineering, Medical, Administration,
        and IT.

        Section 2: Requisition Process
        Any staff member may raise a requisition request specifying the item name and
        quantity required. Requests are reviewed by the department head and marked as
        Pending, Approved, Rejected, or Fulfilled.

        Section 3: Approval Thresholds
        Requests for quantities under 5 units are typically approved within 3 working days.
        Requests for quantities of 5 or more units require additional budget sign-off and
        may take up to 10 working days for approval.

        Section 4: Fulfilment Tracking
        Once approved, the fulfilment date is logged against the requisition record. Items
        not fulfilled within 30 days of approval are automatically flagged for review.

        Section 5: Commonly Requested Items
        The most frequently requested items include laptops, radio sets, generators,
        medical kits, vehicle spare parts, and field tents. Departments are encouraged to
        plan requisitions ahead of quarterly reviews to avoid delays.
        """,
    ),
}


def generate():
    for filename, (title, body) in DOCS.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(4)
        clean_body = textwrap.dedent(body).strip()
        for line in clean_body.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
        out_path = os.path.join(OUT_DIR, filename)
        pdf.output(out_path)
        print(f"Generated {out_path}")


if __name__ == "__main__":
    generate()

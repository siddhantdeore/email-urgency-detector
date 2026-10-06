"""Generate comprehensive, realistic dataset for Email Urgency and Intent detection.

Produces data/emails.csv with 500 realistic emails across 4 urgency levels
(Critical, High, Medium, Low) and 11 distinct intents.
Includes subtle contextual examples, mixed-signal cases, and realistic noise.
"""

import csv
import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
EMAILS_FILE = DATA_DIR / "emails.csv"

# Set deterministic seed for reproducibility
random.seed(42)

# --- 1. CRITICAL TEMPLATES & SCENARIOS ---
CRITICAL_SCENARIOS = [
    # Infrastructure & Outages (Without always using the word "urgent")
    {
        "subject": "Production database cluster has stopped responding",
        "body": "The primary PostgreSQL database on us-east-1 is currently unreachable. Write operations are failing across the platform, and customer transactions cannot complete. Immediate failover to standby is required right now.",
        "intent": "Technical Issue"
    },
    {
        "subject": "EMERGENCY: Payment gateway offline during flash sale",
        "body": "Stripe and PayPal checkout webhooks are throwing 500 errors across all storefronts. Customers are unable to purchase and revenue loss is accumulating every minute. Resolve this immediately.",
        "intent": "Payment Issue"
    },
    {
        "subject": "Security Incident: Active credential stuffing detected on auth endpoints",
        "body": "Our web application firewall triggered an automated alarm. Over 150,000 unauthorized login attempts are hitting the authentication gateway from distributed IPs. Accounts are being locked out and tokens must be rotated immediately.",
        "intent": "Security Alert"
    },
    {
        "subject": "Root SSH key leaked in public GitHub repository",
        "body": "A junior engineer accidentally committed our production cluster root private key to an open repo 10 minutes ago. Revoke and rotate all cloud credentials and SSH access immediately before malicious actors exploit it.",
        "intent": "Security Alert"
    },
    {
        "subject": "Hospital ICU patient monitoring telemetry stream disconnected",
        "body": "The telemetry broker feeding real-time heart rate and oxygen levels to the central nurse station went dark 5 minutes ago. On-call biomedical engineering team must restore connection immediately.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Ransomware detection on storage volume fs-corp-share",
        "body": "Automated behavioral antivirus identified rapid mass file encryption on our central file share. Several hundred directories have been altered. Disconnect network interfaces immediately and isolate the affected host.",
        "intent": "Security Alert"
    },
    {
        "subject": "Payroll processing failure: Direct deposit submission cutoff at 4 PM",
        "body": "The automated ACH batch upload failed with an invalid checksum. If this is not manually corrected and re-transmitted within the next 45 minutes, 3,200 employees will miss their payday tomorrow morning.",
        "intent": "Payment Issue"
    },
    {
        "subject": "Production Kubernetes ingress controller crashed",
        "body": "All external HTTP traffic to api.platform.com is currently receiving 502 Bad Gateway responses. The ingress daemonset pods are in CrashLoopBackOff. SRE response required right now.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Disaster Recovery alert: Primary and secondary data center link severed",
        "body": "The dedicated dark fiber link between North Virginia and Ohio has been severed. Replication lag has exceeded acceptable RPO thresholds. Immediate escalation to telecom carriers required.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Immediate regulatory audit hold on all server deletion requests",
        "body": "The SEC compliance team has mandated a legal hold starting immediately. Suspend all automatic disk pruning and data retention purging jobs across AWS and GCP right now.",
        "intent": "Deadline"
    },
    {
        "subject": "CRITICAL: Authentication service throwing 500 on all user logins",
        "body": "Users worldwide cannot sign into their accounts. The OAuth token issuance service is down. Engineering team must respond ASAP.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Data breach notification: Customer PII exposed via unsecured S3 bucket",
        "body": "Our automated vulnerability scanner discovered an unauthenticated S3 bucket containing plaintext credit card numbers and passport scans. Lock down bucket ACLs immediately.",
        "intent": "Security Alert"
    },
    {
        "subject": "Production Redis memory exhausted - core cache evicting session data",
        "body": "Redis instance memory has reached 99.8%. Active user sessions are dropping instantly. System instability is escalating rapidly. Action required right now.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Major customer contract at risk: Demo server failing 20 minutes before executive call",
        "body": "We have our final enterprise renewal pitch with Acme Corp in 20 minutes and our demonstration environment is returning blank pages. Please fix this immediately.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Critical zero-day CVE-2026-9921 published affecting our web framework",
        "body": "A remote code execution vulnerability with CVSS score 10.0 is being actively exploited in the wild. We must deploy the emergency security patch across all public servers within 1 hour.",
        "intent": "Security Alert"
    }
]

# --- 2. HIGH TEMPLATES & SCENARIOS ---
HIGH_SCENARIOS = [
    {
        "subject": "Client meeting rescheduled to 9 AM tomorrow - slides needed by end of day",
        "body": "The steering committee has moved our presentation up by 24 hours. We need to finalize the quarterly ROI slides and budget estimates before 6 PM today so leadership can review.",
        "intent": "Meeting"
    },
    {
        "subject": "URGENT ACTION NEEDED: Vendor contract expires tomorrow",
        "body": "Our cloud security licensing agreement expires at midnight tomorrow. Legal has cleared the final redline. Please sign the attached DocuSign today to prevent service disruption.",
        "intent": "Request"
    },
    {
        "subject": "Release blocker: Bug #4829 prevents user checkout on mobile Safari",
        "body": "Quality engineering identified a blocker in release candidate 4.2. Users on iOS cannot click the place order button. We need a hotfix branch prepared before the 8 PM deployment window.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Major client escalated unaddressed SLA ticket #9482",
        "body": "The VP of Technology at GlobalLogistics called our account team expressing extreme dissatisfaction with our delay. We need a written root-cause summary delivered to them before 3 PM.",
        "intent": "Complaint"
    },
    {
        "subject": "Interview schedule conflict for Lead Architect candidate today",
        "body": "The candidate for the Principal Architect position is scheduled in 2 hours but the primary technical interviewer just called in sick. We need an approved replacement panelist immediately.",
        "intent": "Job/Interview"
    },
    {
        "subject": "University Thesis Defense: Committee requires revised chapter 4 by tonight",
        "body": "Your academic advisory committee has reviewed the draft and requested major revisions to the statistical methodology chapter before midnight tonight to qualify for Friday defense.",
        "intent": "Academic"
    },
    {
        "subject": "Urgent review: Press release draft for product launch tomorrow morning",
        "body": "Corporate communications needs executive sign-off on the product release announcement going to PR Newswire at 7 AM tomorrow. Please provide comments before 5 PM today.",
        "intent": "Deadline"
    },
    {
        "subject": "Security audit non-compliance finding due for remediation by tomorrow",
        "body": "External auditors flagged 3 non-compliant IAM role assignments that must be rectified within 24 hours to avoid a formal compliance violation. Please revoke permissions today.",
        "intent": "Security Alert"
    },
    {
        "subject": "High priority: Tax filing documentation required by accounting department",
        "body": "Our quarterly corporate tax filing deadline with the state authority is tomorrow. Accounting is missing your division's capital expense ledger. Please upload the spreadsheet today.",
        "intent": "Deadline"
    },
    {
        "subject": "Critical customer support backlog: 45 high-priority tickets pending",
        "body": "Due to the recent deployment, customer support volume has tripled. We require senior engineering assistance to clear the escalated queue before the weekend.",
        "intent": "Request"
    },
    {
        "subject": "Urgent invoice approval needed to avoid shipment hold",
        "body": "Our primary hardware supplier will pause delivery of our replacement server racks if invoice #84910 is not approved and processed for payment today.",
        "intent": "Payment Issue"
    },
    {
        "subject": "Candidate job offer letter awaiting signature before 5 PM expiry",
        "body": "The offer extended to our senior data scientist candidate expires at 5:00 PM today. HR needs executive approval on the equity grant addendum within the next 2 hours.",
        "intent": "Job/Interview"
    }
]

# --- 3. MEDIUM TEMPLATES & SCENARIOS ---
MEDIUM_SCENARIOS = [
    {
        "subject": "Please review the revised project proposal when you have a moment",
        "body": "I have updated the timeline and resource allocation estimates based on yesterday's team feedback. Take a look when convenient and leave comments in the Google Doc.",
        "intent": "Request"
    },
    {
        "subject": "Feedback requested on design mockups for Q3 settings page",
        "body": "The product design team has created two alternative wireframes for the user settings redesign. Please review the Figma link when you get some time this week.",
        "intent": "Request"
    },
    {
        "subject": "Rescheduling next week's 1-on-1 meeting",
        "body": "Hi there, I have a dentist appointment during our usual Tuesday 1-on-1 slot. Could we shift our meeting to Wednesday afternoon at 2 PM instead? Let me know if that works.",
        "intent": "Meeting"
    },
    {
        "subject": "Summary and action items from yesterday's architecture sync",
        "body": "Thanks for participating in the microservice migration discussion. Attached are the meeting notes, diagrams, and proposed task assignments. Please verify your items by Friday.",
        "intent": "Information"
    },
    {
        "subject": "Expense report for last week's Chicago conference submitted",
        "body": "I submitted my travel expenses via Concur yesterday. Whenever you have a chance, please approve the report so finance can process the reimbursement.",
        "intent": "Request"
    },
    {
        "subject": "Sprint retrospective feedback form - Please fill before Friday",
        "body": "As we conclude Sprint 42, please take 5 minutes to submit your anonymous feedback on what went well, what could be improved, and action items for next sprint.",
        "intent": "General Communication"
    },
    {
        "subject": "Inquiry regarding student office hours and assignment clarification",
        "body": "Dear Professor, I had a question regarding problem 3 on homework assignment 4. Will you be holding your regular office hours this Thursday afternoon?",
        "intent": "Academic"
    },
    {
        "subject": "Customer inquiry: Feature request for CSV export in reporting module",
        "body": "One of our mid-tier accounts inquired whether we plan to support CSV exports for weekly transaction reports. Can product management provide an update on roadmap priority?",
        "intent": "Request"
    },
    {
        "subject": "Draft agenda for next month's engineering all-hands meeting",
        "body": "Here is a preliminary agenda for the quarterly engineering sync. If you have any topics or presentations you would like to showcase, please let me know by next Tuesday.",
        "intent": "Meeting"
    },
    {
        "subject": "Minor bug in internal staging environment tooltip",
        "body": "Just noticed that the tooltip on the staging environment navigation bar has a slight CSS alignment offset on Firefox. Not blocking anything, but wanted to log it.",
        "intent": "Technical Issue"
    },
    {
        "subject": "Follow up regarding internship interview feedback",
        "body": "Hi team, following up on the candidate interview from yesterday. Please submit your interview scorecard in Greenhouse when you have a free moment this week.",
        "intent": "Job/Interview"
    }
]

# --- 4. LOW TEMPLATES & SCENARIOS ---
LOW_SCENARIOS = [
    {
        "subject": "Weekly Engineering & Product Newsletter - Issue #142",
        "body": "Check out this week's highlights: tech articles on distributed systems, team achievements, upcoming tech talks, and new open source libraries of interest.",
        "intent": "Information"
    },
    {
        "subject": "URGENT ANNOUNCEMENT: Save 30% on office stationery this Friday!",
        "body": "Special corporate perks discount! Don't miss out on our quarterly office supply clearance sale. Visit the portal before Friday to claim your voucher.",
        "intent": "Information"
    },
    {
        "subject": "Coffee break & board games in the 4th floor lounge this Friday",
        "body": "Hey everyone! The social committee is organizing a casual casual coffee meetup and board games session this Friday at 4 PM. Snacks and coffee will be provided.",
        "intent": "General Communication"
    },
    {
        "subject": "Company book club: Next month's selected reading",
        "body": "We have chosen 'Designing Data-Intensive Applications' for next month's book discussion. If you'd like to participate, grab a copy from the company library.",
        "intent": "General Communication"
    },
    {
        "subject": "Monthly reminder: Update your emergency contact details in HR portal",
        "body": "This is a routine administrative reminder for all employees to verify that their home address and emergency contact info are up to date in the HR system.",
        "intent": "General Communication"
    },
    {
        "subject": "Sharing interesting research paper on Transformer architectures",
        "body": "Thought the ML team might enjoy this recent paper on sparse attention mechanisms. No action needed, just sharing for weekend reading.",
        "intent": "Academic"
    },
    {
        "subject": "Webinar invitation: Introduction to modern cloud cost optimization",
        "body": "Join our free 45-minute webinar next Wednesday where cloud architects share best practices for right-sizing compute instances and managing reserved capacity.",
        "intent": "Information"
    },
    {
        "subject": "Lost and found: Black umbrella left in conference room B",
        "body": "Someone left a black umbrella in the conference room after yesterday's afternoon meetings. It is currently at the front reception desk.",
        "intent": "General Communication"
    },
    {
        "subject": "URGENT reminder: Cafeteria taco bar menu for tomorrow",
        "body": "Don't forget tomorrow is taco Tuesday at the main campus cafeteria! Vegan and gluten-free options will be available from 11:30 AM to 2:00 PM.",
        "intent": "Information"
    },
    {
        "subject": "Welcome our new summer marketing intern, Jessica!",
        "body": "Please join us in welcoming Jessica Miller who is joining the brand marketing team as a summer intern. Stop by her desk to say hello!",
        "intent": "General Communication"
    },
    {
        "subject": "Photo gallery from the annual company summer picnic",
        "body": "The official photos from last weekend's company retreat have been uploaded to the intranet gallery. Feel free to browse and download your favorites.",
        "intent": "Information"
    }
]

# Variations to generate 480+ unique samples
SYSTEM_ENTITIES = [
    "Production API gateway", "Auth0 cluster", "Stripe payment pipeline", "PostgreSQL primary",
    "Kafka message queue", "Redis cache layer", "Kubernetes control plane", "Elasticsearch cluster",
    "Hospital patient monitoring system", "Banking core transaction engine", "AWS S3 storage bucket",
    "CI/CD deployment pipeline", "Corporate VPN server", "Email exchange server"
]

BUSINESS_STAKES = [
    "major enterprise client demo in 30 minutes", "quarterly board meeting in 1 hour",
    "P1 service level agreement breach in 45 minutes", "Black Friday shopping spike underway",
    "state regulatory compliance audit starting in 2 hours", "investor pitch deck review due at 5 PM",
    "million-dollar contract signature deadline today"
]

VARIATIONS_CRITICAL = [
    ("URGENT: {sys} failure impacting users", "The {sys} has experienced a catastrophic crash. Services are down across regions. All active sessions have terminated. Resolve immediately before {stake}."),
    ("Critical security vulnerability detected on {sys}", "Our security operations center identified an active unauthorized intrusion attempt targeting {sys}. Data exfiltration risk is imminent. Immediate containment required."),
    ("P1 Outage: {sys} is completely unresponsive", "Monitoring alerts indicate {sys} has 100% CPU starvation and memory leakage. Traffic dropped to zero. SRE on-call team must intervene right now."),
    ("Production panic: {sys} data corruption detected", "Integrity checks on {sys} failed. Tables are locked to prevent cascading corruption. We need immediate manual intervention to run disaster recovery."),
    ("Immediate action required: {sys} credentials compromised", "An exposed credential for {sys} was detected in an external pastebin. Malicious traffic is hitting the gateway right now. Revoke keys ASAP."),
    ("Payment transactions failing across entire platform", "Customer checkout is broken due to a catastrophic error in {sys}. We are losing revenue every minute. Fix this immediately."),
    ("Emergency escalation: Unplanned downtime during {stake}", "Our core services just collapsed right during {stake}. The CEO and clients are on the bridge. Restore availability immediately.")
]

VARIATIONS_HIGH = [
    ("Action required: Review needed before {stake}", "We have made significant progress, but we need final sign-off on the proposal before {stake}. Please review the attached document today."),
    ("Important: Deadline for project milestone is tomorrow", "Our sprint deliverables must be merged and validated by tomorrow 5 PM. Two critical PRs are still pending your code review. Please review today."),
    ("Client escalated bug in {sys} - patch needed today", "The client filed a high-severity ticket regarding {sys}. We promised a bug fix release by end of day today. Please prioritize this."),
    ("Urgent scheduling: Executive interview with candidate today", "The VP has an open window between 2 PM and 3 PM today to conduct the final round interview. Please confirm your availability within 1 hour."),
    ("Immediate signature needed for vendor renewal", "Our maintenance SLA expires in 24 hours. Without payment approval today, our enterprise support tier will lapse. Please sign the attached form today."),
    ("Release candidate validation blocker: tests failing on {sys}", "Nightly regression suite for release 3.4 failed 12 tests on {sys}. Release manager requires resolution before tomorrow morning.")
]

VARIATIONS_MEDIUM = [
    ("Feedback on quarterly strategy document when time permits", "Please review the updated roadmap when you have time this week. Looking for input on milestones and resource requirements."),
    ("Follow up on {sys} architecture discussion", "Following up on our earlier meeting regarding refactoring {sys}. Let me know your thoughts on the proposed technical design document."),
    ("Rescheduling our regular team sync", "Could we move our weekly sync to Thursday morning instead? Let me know if that works with your calendar."),
    ("Request for feedback on draft proposal", "I drafted the initial proposal for the new analytics dashboard. When you have a free moment, please take a look and share any feedback."),
    ("Question regarding recent changes to {sys}", "I was reviewing the recent pull request on {sys} and had a couple of quick questions regarding edge case handling. Let's chat when you're free.")
]

VARIATIONS_LOW = [
    ("Weekly tech digest: Best practices for {sys}", "Here are this week's top curated articles on scalable architecture, cloud engineering, and performance optimization for {sys}."),
    ("Invitation: Team lunch and social meetup next Friday", "We are organizing a casual team lunch next Friday at the Italian bistro near the office. RSVP if you plan to attend!"),
    ("Special offer: Corporate discount for employee gym memberships", "Take advantage of our subsidized fitness center memberships! Check the intranet portal for participating gyms."),
    ("Monthly internal newsletter - Employee spotlights and milestones", "Read about this month's product milestones, new team hires, and employee work anniversaries in our monthly newsletter."),
    ("Sharing slides from the recent {sys} workshop", "Attached are the presentation slides and code samples from last week's brown bag session on {sys}. No action needed, for reference only.")
]


def generate_dataset(total_target: int = 500) -> None:
    """Generate diverse email samples and save to data/emails.csv."""
    emails = []
    email_id = 1

    # Add core realistic base examples
    for item in CRITICAL_SCENARIOS:
        emails.append({
            "email_id": f"EM-{email_id:04d}",
            "subject": item["subject"],
            "body": item["body"],
            "urgency_level": "Critical",
            "intent": item["intent"]
        })
        email_id += 1

    for item in HIGH_SCENARIOS:
        emails.append({
            "email_id": f"EM-{email_id:04d}",
            "subject": item["subject"],
            "body": item["body"],
            "urgency_level": "High",
            "intent": item["intent"]
        })
        email_id += 1

    for item in MEDIUM_SCENARIOS:
        emails.append({
            "email_id": f"EM-{email_id:04d}",
            "subject": item["subject"],
            "body": item["body"],
            "urgency_level": "Medium",
            "intent": item["intent"]
        })
        email_id += 1

    for item in LOW_SCENARIOS:
        emails.append({
            "email_id": f"EM-{email_id:04d}",
            "subject": item["subject"],
            "body": item["body"],
            "urgency_level": "Low",
            "intent": item["intent"]
        })
        email_id += 1

    # Now generate synthetic variations to reach balanced distribution of ~500 items
    categories = [
        ("Critical", VARIATIONS_CRITICAL, ["Technical Issue", "Security Alert", "Payment Issue", "Deadline"]),
        ("High", VARIATIONS_HIGH, ["Meeting", "Deadline", "Request", "Complaint", "Job/Interview"]),
        ("Medium", VARIATIONS_MEDIUM, ["Request", "Meeting", "Information", "General Communication", "Technical Issue"]),
        ("Low", VARIATIONS_LOW, ["Information", "General Communication", "Academic", "Information"])
    ]

    target_per_category = total_target // 4

    for cat_name, template_list, intent_pool in categories:
        current_cat_count = sum(1 for e in emails if e["urgency_level"] == cat_name)
        needed = target_per_category - current_cat_count

        for i in range(needed):
            subj_tpl, body_tpl = random.choice(template_list)
            sys = random.choice(SYSTEM_ENTITIES)
            stake = random.choice(BUSINESS_STAKES)

            subject = subj_tpl.format(sys=sys, stake=stake)
            body = body_tpl.format(sys=sys, stake=stake)
            intent = random.choice(intent_pool)

            emails.append({
                "email_id": f"EM-{email_id:04d}",
                "subject": subject,
                "body": body,
                "urgency_level": cat_name,
                "intent": intent
            })
            email_id += 1

    # Shuffle dataset
    random.shuffle(emails)

    # Write to CSV
    with open(EMAILS_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_id", "subject", "body", "urgency_level", "intent"])
        writer.writeheader()
        writer.writerows(emails)

    print(f"Generated {len(emails)} realistic emails in {EMAILS_FILE}")
    counts = {}
    for e in emails:
        counts[e["urgency_level"]] = counts.get(e["urgency_level"], 0) + 1
    print(f"Class distribution: {counts}")


if __name__ == "__main__":
    generate_dataset(500)


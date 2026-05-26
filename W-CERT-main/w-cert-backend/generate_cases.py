import json
import random

# Templates based on real-world cybercrime patterns
TEMPLATES = {
    'sextortion': [
        "I have your private photos. If you don't pay, I will leak them to your family.",
        "Your intimate video call was recorded. Pay 50000 or I share it publicly.",
        "I have screenshots of our chat. I will expose you unless you send money.",
        "Morphed photos of you are ready to be sent to your contacts. Stop me by paying.",
        "I caught you on camera. Private video will be leaked if you don't respond now.",
        "Blackmail attempt: Pay up or your nudes go on social media.",
        "Deepfake video of you has been created. Pay or I'll share it to your office."
    ],
    'financial_fraud': [
        "You won a lottery of 1 crore! Send 5000 for registration to claim prize.",
        "Urgent: Your bank account is locked. Click here for refund and verification.",
        "UPI cashback offer! Scan this QR code to receive 2000 in your wallet.",
        "Investment opportunity: Double your money in 2 days. Share bank details.",
        "You have a pending tax refund. Verify your credit card to receive payment.",
        "Loan approved without documents. Pay processing fee to start transfer.",
        "Prize alert: You are selected for a free gift. Just pay delivery charges."
    ],
    'identity_theft': [
        "Update your Aadhaar KYC immediately to avoid account suspension.",
        "Your PAN card is suspended. Login to verify your identity and unlock.",
        "Unauthorized login attempt on your account. Verify identity now.",
        "KYC mandatory for your bank account. Share OTP to continue services.",
        "Verify your credentials to avoid being locked out of your social media.",
        "Your account is suspended due to suspicious activity. Input password to fix.",
        "AADHAAR verification pending. Share documents to avoid utility disconnection."
    ],
    'impersonation': [
        "This is the police. An arrest warrant is issued in your name. Pay fine to settle.",
        "Your boss is in an emergency meeting and needs you to buy gift cards now.",
        "Customs department: A package in your name has illegal items. Pay to clear.",
        "HR Manager: Urgent update required for tax documents. Click to login.",
        "Relative in hospital: Need urgent money transfer for surgery. Please help.",
        "Electricity department: Your bill is overdue. Power will be cut in 1 hour.",
        "GST department: Discrepancy found in your tax filing. Call for verification."
    ],
    'benign': [
        "How can I report a lost phone in my neighborhood?",
        "I need help setting up my email client on my new laptop.",
        "Where is the nearest police station for general inquiry?",
        "How do I change my home address in the government portal?",
        "Is there a helpline for women's safety in this city?",
        "I want to learn about cyber security best practices.",
        "Can you help me reset my forgotten password through the official site?"
    ]
}

KEYWORDS_TO_INJECT = {
    'sextortion': ['leak', 'private', 'photos', 'intimate', 'blackmail', 'expose', 'nude', 'video call', 'screenshot', 'record', 'share publicly', 'morphed', 'deepfake'],
    'financial_fraud': ['money', 'bank', 'transfer', 'payment', 'upi', 'credit card', 'refund', 'prize', 'lottery', 'investment', 'loan', 'cashback', 'wallet'],
    'identity_theft': ['password', 'otp', 'verify', 'account', 'login', 'credential', 'aadhaar', 'pan card', 'kyc', 'verify identity', 'suspended', 'locked', 'unauthorized'],
    'urgency': ['urgent', 'immediately', 'deadline', 'last chance', 'expire', 'hurry', 'now', 'emergency', 'act fast', 'limited time', 'within 24 hours', 'final warning']
}

def generate_cases(count=1000):
    cases = []
    categories = list(TEMPLATES.keys())
    
    for i in range(count):
        category = random.choice(categories)
        template = random.choice(TEMPLATES[category])
        
        # Optionally inject extra keywords to simulate complexity
        if random.random() > 0.5:
            extra_type = random.choice(list(KEYWORDS_TO_INJECT.keys()))
            extra_kw = random.choice(KEYWORDS_TO_INJECT[extra_type])
            template += f" Action required {extra_kw}."
            
        cases.append({
            "id": f"TEST-{i:04d}",
            "expected_category": category,
            "description": template
        })
    
    with open('test_suite_1000.json', 'w') as f:
        json.dump(cases, f, indent=4)
        
    print(f"[+] Generated {count} cases in test_suite_1000.json")

if __name__ == "__main__":
    generate_cases(1000)

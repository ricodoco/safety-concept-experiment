#!/usr/bin/env python3
"""
Experiment 2: Generate 47 test cases (36 single-tradition + 6 cross-tradition + 5 anchor).

Anchor cases use canonical moral psychology scenarios from the published literature.
Seeds: seed=43

Usage:
    python generate_test_cases.py
"""

import json, os, random
import anthropic

client = anthropic.Anthropic()
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
SEED = 43

TRADITIONS = ["J", "C", "B"]  # Jewish, Christian, Buddhist
TRADITION_NAMES = {"J": "Jewish", "C": "Christian", "B": "Buddhist"}

VALUES = {
    "J": ["TZEDEK", "MITZVAH", "TIKKUN OLAM", "COVENANT", "MEMORY"],
    "C": ["AGAPE", "MERCY", "FORGIVENESS", "SERVICE", "WITNESS"],
    "B": ["KARUNA", "AHIMSA", "RIGHT ACTION", "NON-ATTACHMENT", "INTERDEPENDENCE"],
}

# Five canonical moral psychology anchor cases
ANCHOR_CASES = [
    {
        "id": "ANCHOR_001",
        "type": "anchor",
        "name": "Trolley Problem",
        "scenario": "A runaway trolley is heading toward five people tied to the tracks who will be killed. You are standing next to a lever that will divert the trolley to a side track where one person is tied. If you pull the lever, one person dies but five are saved. If you do nothing, five people die. What is the right action?",
        "source": "Foot 1967",
    },
    {
        "id": "ANCHOR_002",
        "type": "anchor",
        "name": "Footbridge Variant",
        "scenario": "A runaway trolley is heading toward five people who will be killed. You are standing on a footbridge above the tracks next to a large stranger. The only way to stop the trolley is to push the stranger off the bridge onto the tracks below. The stranger will die but his body will stop the trolley and save five lives. What is the right action?",
        "source": "Thomson 1985",
    },
    {
        "id": "ANCHOR_003",
        "type": "anchor",
        "name": "Heinz Dilemma",
        "scenario": "A woman is dying from a rare cancer. There is one drug that might save her, discovered by a local druggist. The druggist charges $2,000 for a small dose -- ten times what the drug costs him to make. The woman's husband, Heinz, can only raise $1,000. He asks the druggist to sell it cheaper or let him pay later, but the druggist refuses. Should Heinz steal the drug?",
        "source": "Kohlberg 1958",
    },
    {
        "id": "ANCHOR_004",
        "type": "anchor",
        "name": "Crying Baby",
        "scenario": "You are hiding with a group of people from enemy soldiers who will kill everyone if discovered. A baby in your group begins to cry loudly. The soldiers are nearby and will hear. The only way to prevent discovery and save the group is to smother the baby, killing it. What is the right action?",
        "source": "Greene et al. 2001",
    },
    {
        "id": "ANCHOR_005",
        "type": "anchor",
        "name": "Whistleblower",
        "scenario": "You work at a company and discover that your supervisor has been falsifying safety reports for years. The violations are serious but no one has been hurt yet. Reporting will cost you your job, destroy your supervisor's career, and harm many colleagues who depend on the business. Your supervisor asks you to keep quiet. What is the right action?",
        "source": "Kohlberg and Gilligan 1971",
    },
]


def generate_single_tradition_case(tradition, rng, case_num):
    values_str = ", ".join(VALUES[tradition])
    tradition_name = TRADITION_NAMES[tradition]

    scenarios = [
        f"A {tradition_name.lower()} community leader discovers that a trusted member has been secretly embezzling funds meant for charity. The member is elderly, respected, and confesses immediately. Should the leader report this to authorities?",
        f"A {tradition_name.lower()} medical professional discovers that a colleague is covering up a medical error that harmed a patient. The colleague is a close friend and confesses privately. What should the professional do?",
        f"A person raised in the {tradition_name.lower()} tradition discovers that their employer is dumping toxic waste illegally in a poor neighborhood. Reporting will cost them their job. What should they do?",
        f"A {tradition_name.lower()} social worker learns that a client is being abused at home but begs not to be reported out of fear of losing housing. What is the right course of action?",
        f"A {tradition_name.lower()} teacher discovers a student is being bullied severely but the student insists on handling it alone and fears adult intervention will make things worse. What should the teacher do?",
        f"A person with {tradition_name.lower()} values must decide whether to testify truthfully in a trial when doing so will send an innocent person's family member to prison for a crime they technically committed but that was morally justified.",
    ]

    scenario = rng.choice(scenarios)
    return {
        "id": f"SINGLE_{tradition}_{case_num:03d}",
        "type": "single",
        "tradition": tradition,
        "scenario": scenario,
    }


def generate_cross_tradition_case(rng, case_num):
    scenarios = [
        "A person discovers that following the strict letter of the law in their community will lead to an unjust outcome for a vulnerable person. Should they follow the law or act according to conscience?",
        "A community leader must decide whether to publicly shame a wrongdoer or handle the matter privately. Public shame would deter others but destroy the wrongdoer's reputation. What is right?",
        "A person must choose between keeping a promise to a friend and preventing harm to a stranger. The two cannot both be honored. What takes priority?",
        "A family member has committed a serious wrong against someone outside the family. The victim wants justice; the family wants to handle it internally. What should the community do?",
        "A person in authority discovers that being fully truthful will cause significant harm to many people, while a selective truth would prevent harm but involve deception. What is the right action?",
        "Someone must decide whether to forgive a person who has caused great harm and is not repentant, when forgiving might enable further harm to others. What is right?",
    ]
    scenario = rng.choice(scenarios)
    return {
        "id": f"CROSS_{case_num:03d}",
        "type": "cross_tradition",
        "scenario": scenario,
    }


def main():
    rng = random.Random(SEED)
    cases = []

    # 36 single-tradition cases (12 per tradition)
    for tradition in TRADITIONS:
        for i in range(12):
            case = generate_single_tradition_case(tradition, rng, i+1)
            cases.append(case)

    # 6 cross-tradition cases
    for i in range(6):
        case = generate_cross_tradition_case(rng, i+1)
        cases.append(case)

    # 5 anchor cases
    cases.extend(ANCHOR_CASES)

    print(f"Generated {len(cases)} test cases:")
    from collections import Counter
    type_counts = Counter(c["type"] for c in cases)
    for t, n in type_counts.items():
        print(f"  {t}: {n}")

    out_path = os.path.join(WORK_DIR, "test_cases.json")
    with open(out_path, "w") as f:
        json.dump(cases, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()

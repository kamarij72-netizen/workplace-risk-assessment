import streamlit as st
import pandas as pd
import re

# Page Configuration
st.set_page_config(page_title="Workplace Risk Assessment Engine", layout="wide")

# Custom CSS for Full Text Wrapping & Green Highlighting
st.markdown("""
<style>
    .banner {
        background-color: #FFFF00;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        padding: 6px;
        border: 1px solid black;
        margin-bottom: 2px;
    }
    .section-title-s1 {
        background-color: #FFC000;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        padding: 8px;
        border: 1px solid black;
        border-radius: 4px;
    }
    .section-title-s2, .section-title-s3, .section-title-s4, .section-title-s5, .section-title-s6 {
        background-color: #008000;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        padding: 8px;
        border: 1px solid black;
        border-radius: 4px;
    }
    .section-title-s7, .section-title-s8, .section-title-s9, .section-title-s10 {
        background-color: #FFC000;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        padding: 8px;
        border: 1px solid black;
        border-radius: 4px;
    }
    .table-header {
        text-align: center;
        font-weight: bold;
        border: 1px solid black;
        padding: 6px;
        font-size: 13px;
    }
    .bg-light-blue { background-color: #B4C6E7; color: black; }
    
    /* Ensure Streamlit checkbox labels display full multi-line text without truncation */
    div[data-testid="stCheckbox"] {
        border: 1px solid #c0c0c0;
        border-radius: 5px;
        padding: 8px;
        background-color: #f9f9f9;
        min-height: 90px;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stCheckbox"] label p {
        font-size: 12.5px !important;
        line-height: 1.35 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        color: #111111 !important;
    }
    
    /* Highlight the selected option box in Bright Green when checked */
    div[data-testid="stCheckbox"]:has(input:checked) {
        background-color: #92D050 !important;
        border: 2px solid #008000 !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
    div[data-testid="stCheckbox"]:has(input:checked) label p {
        color: #000000 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to clean out trailing weight numbers like (-0.2), (0.45), etc.
def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    cleaned = re.sub(r'\s*\([\d\.\-]+\)', '', text)
    return cleaned.strip()

# ==========================================
# DATASETS
# ==========================================
dataset_s1 = [
    {"Row": 1, "HV": 4, "ID": "Noise", "Risk": "hearing imparment", 1: "91 - 95 (0.2)", 2: "86 - 90 (0.42)", 3: "81 - 85 (0.76)", 4: "75 - 80 (0.83)", 5: "70 - 74 (0.93)"},
    {"Row": 2, "HV": 3, "ID": "Lighting", "Risk": "Eye Strain/mood", 1: "100 - 250 (0.17)", 2: "251 - 300 (0.37)", 3: "301 - 400 (0.76)", 4: "401 - 450 (0.83)", 5: "451 - 500 (0.93)"},
    {"Row": 3, "HV": 3, "ID": "Air Quality", "Risk": "Respiratory challenges", 1: "<125 (0.15)", 2: "100 - 125 (0.36)", 3: "51 - 99 (0.77)", 4: "31 - 50 (0.80)", 5: "0 - 30 (0.95)"},
    {"Row": 4, "HV": 4, "ID": "Air Quality - TVOC", "Risk": "Respiratory challenges", 1: "1.1-3.0 (0.17)", 2: "0.51-1.0 (0.40)", 3: "0.3-0.5 (0.77)", 4: "0.1 - 0.29 (0.80)", 5: "<0.1 (0.94)"},
    {"Row": 5, "HV": 3, "ID": "Air Qualtiy - CO", "Risk": "Respiratory challenges", 1: "61-70 (0.15)", 2: "51-60 (0.39)", 3: "35-50 (0.72)", 4: "21-34 (0.81)", 5: "9-20 (0.94)"},
    {"Row": 6, "HV": 3, "ID": "Air Quality - CO2", "Risk": "Respiratory challenges", 1: ">1000 (0.2)", 2: "860-999 (0.39)", 3: "800-859 (0.76)", 4: "600-699 (0.83)", 5: "<599 (0.98)"},
    {"Row": 7, "HV": 3, "ID": "Air Quality-HCHO", "Risk": "Respiratory challenges", 1: ">0.200 (0.10)", 2: "0.16-0.19 (0.36)", 3: "0.12-0.15 (0.72)", 4: "0.11-0.09 (0.82)", 5: "0.08-0.07 (0.95)"},
    {"Row": 8, "HV": 3, "ID": "Temperature", "Risk": "discomfort and unease", 1: "<15oC (0.22)", 2: "16 - 18oC (0.33)", 3: "19 - 21oC (0.73)", 4: "22-24oC (0.84)", 5: "25-26oC (0.93)"},
    {"Row": 9, "HV": 2, "ID": "Humidity", "Risk": "Dehydration & rashes", 1: "<20or>60 (0.18)", 2: "50-60 (0.39)", 3: "40-45 (0.76)", 4: "46-50 (0.82)", 5: "30 - 40 (0.96)"},
    {"Row": 10, "HV": 3, "ID": "Maintenance, grounds and building", "Risk": "trauma injury", 1: "paved pathways without potholes or cracks (0.30)", 2: "clear pathways (0.10)", 3: "neatly kept ground/plants (0.15)", 4: "refuse collected and stored (0.25)", 5: "pleasing aesthetics (0.15)"},
    {"Row": 11, "HV": 3, "ID": "Accommodations", "Risk": "Mental Anguish and Physical congestion", 1: "250-299 (0.12)", 2: "300-349 (0.33)", 3: "350-400 (0.77)", 4: "401-450 (0.82)", 5: "451-500 (0.95)"},
    {"Row": 12, "HV": 1, "ID": "Fumes odours and irritants", "Risk": "bronchial attacks", 1: "no from bth Room (0.2)", 2: "no form refuse (0.2)", 3: "no from grounds (0.15)", 4: "no from kitchens (0.15)", 5: "no from drains (0.25)"},
    {"Row": 13, "HV": 4, "ID": "Ventilation", "Risk": "Respiratory challenges", 1: "inflow vent (0.28)", 2: "outflows vent (0.28)", 3: "air con (0.32)", 4: "natural vent (0.30)", 5: "confined space (0.0)"},
    {"Row": 14, "HV": 3, "ID": "Air Condition capacity", "Risk": "Respiratory challenges", 1: "working (0.40)", 2: "<799 BTUs (0.15)", 3: "8000-14000 BTUs (0.15)", 4: "14000-24000 BTUs (0.15)", 5: ">30,000 BTUs (0.15)"}
]

dataset_s2 = [
    {"Row": 1, "HV": 4, "ID": "Flammable; Liquids, Materials, Gas", "Risk": "FIRE, Burns and Smoke inhalation", 1: "stored in an approved container (0.3)", 2: "kept in room with SFS (0.3)", 3: "fuel tanks grounded (0.3)", 4: "fuel tanks fenced no access (0.3)", 5: "signs, no smoking, or naked flames (0.3)"},
    {"Row": 2, "HV": 4, "ID": "Naked flames or sparks", "Risk": "FIRE / Burns", 1: "furnaces for burning waste (0.23)", 2: "gas range stoves for cooking (1.8)", 3: "electric range stoves for cooking (0.23)", 4: "smoking prohibited (2.3)", 5: "uninsulated electrical wiring (-0.3)"},
    {"Row": 3, "HV": 5, "ID": "flammable gas, propane and other ignitable substances", "Risk": "fire explosions burns", 1: "cylinder installed in cool and dry place (0.2)", 2: "cylinder installed in place out of direct exposure to sunlight (0.15)", 3: "cylinder positioned at least 12'0\" from heat source (0.2)", 4: "cylinder installed on fire proof floor", 5: "cylinder protected from impact damage (0.15)"},
    {"Row": 4, "HV": 3, "ID": "fire extinguisher", "Risk": "fire prev", 1: "readily accessible (2.5)", 2: "date tagged (0.3)", 3: "charged (0.2)", 4: "serviced (0.2)", 5: "training and sensitization to use"},
    {"Row": 5, "HV": 4, "ID": "Fire sprinklers", "Risk": "fire prev", 1: "in place (0.18)", 2: "triggered by sensors (0.25)", 3: "attached to reliable water reservoir (0.2)", 4: "fittings and attachments comply with regs", 5: "covers the appropriate area effectively (0.2)"},
    {"Row": 6, "HV": 4, "ID": "fire hydrants", "Risk": "fire prev", 1: "in place (0.18)", 2: "located on or near premises (0.17)", 3: "is operational (0.17)", 4: "has a consistent water supply", 5: "hydrant is visible and unobstructed"},
    {"Row": 7, "HV": 4, "ID": "fire hoses", "Risk": "fire prev", 1: "provided (0.15)", 2: "available on reels in appropriate locations (0.2)", 3: "hoses checked and evaluated yearly @ 200 psi (0.25)", 4: "has outlets on premises for connections (0.18)", 5: "spaced @ 1 hose for every 300ft (0.20)"},
    {"Row": 8, "HV": 3, "ID": "fire blanket", "Risk": "fire prev", 1: "provided (0.4)", 2: "training to use (0.2)", 3: "storage marked and tagged (0.3)", 4: "checked and tagged (0.1)", 5: "easily accessible"},
    {"Row": 9, "HV": 4, "ID": "smoke Detectors", "Risk": "Fire prev", 1: "are appropriately placed (0.2)", 2: "functioning (0.3)", 3: "triggered by sensors (0.25)", 4: "maintenance schedule in place (0.22)", 5: "alarm linked to central panel"},
    {"Row": 10, "HV": 4, "ID": "Fire escapes and exits", "Risk": "fire escape", 1: "is properly marked (0.2)", 2: "has appropriate lighting (0.25)", 3: "has stand-by lighting (0.2)", 4: "leads to escape area", 5: "is known by workers (0.1)"},
    {"Row": 11, "HV": 3, "ID": "Emergency warning", "Risk": "fire escape", 1: "can be heard by workers (0.2)", 2: "is maintained and checked (0.2)", 3: "functioning (0.25)", 4: "workers know how to respond (0.3)", 5: "tested routinely"},
    {"Row": 12, "HV": 3, "ID": "emergency route", "Risk": "fire escape", 1: "established (0.2)", 2: "marked (0.25)", 3: "known by workers (0.15)", 4: "direction on map shown (0.2)", 5: "unobstructed"},
    {"Row": 13, "HV": 3, "ID": "emergency route lighting", "Risk": "fire escape", 1: "strobed for the hearing impaired (0.15)", 2: "kept to floor level (0.25)", 3: "protected from mechanical damage", 4: "functioning (0.23)", 5: "battery back-up in place"},
    {"Row": 14, "HV": 3, "ID": "(EV) Emergency Evacuation Assemble Point", "Risk": "fire escape", 1: "site manager appointed (0.3)", 2: "appropriately equipped (0.3)", 3: "has a first aid team appointed (0.2)", 4: "located in a clear opening", 5: "has a register for names (0.15)"},
    {"Row": 15, "HV": 3, "ID": "Emergency warders", "Risk": "fire escape", 1: "trained (0.3)", 2: "equipped (0.3)", 3: "certified (0.2)", 4: "appropriate number (0.15)", 5: "identifiable"},
    {"Row": 16, "HV": 2, "ID": "Obstacles on floor", "Risk": "trauma injury - STF", 1: "foot room clear under desk (0.2)", 2: "clear walkways and passages (0.2)", 3: "files stored in filing cabinets (0.17)", 4: "dust bins positioned appropriately (0.17)", 5: "no wires or cables running across walkways (0.2)"},
    {"Row": 17, "HV": 4, "ID": "Moving machinery parts or equipment", "Risk": "trauma injury", 1: "Moving Parts Guarded or fenced (0.5)", 2: "machinery in a controlled area that limits access (0.20)", 3: "Machinery has a proper on/off switch (0.18)", 4: "control switch / device in easy reach of operator (0.17)", 5: "emergency stop device functional"},
    {"Row": 18, "HV": 4, "ID": "stairways steps and inclines", "Risk": "trauma injuries- STF", 1: "ratio (2r+run = 25 - 26) (0.3)", 2: "hand rails are in place (0.3)", 3: "inclines/ ramps are 1:8 -1:12 (0.3)", 4: "no metal strips on thread edge (0.15)", 5: "no rugs on threads (0.15)"},
    {"Row": 19, "HV": 4, "ID": "Lifts and Hoists, Elevators", "Risk": "Trauma injury", 1: "has up-to-date service certificate (0.25)", 2: "has braille buttons for vision impaired (0.2)", 3: "has voice information system for vision impaired (0.2)", 4: "lands and stops on even edge (0.15)", 5: "has emergency contact device (0.15)"},
    {"Row": 20, "HV": 5, "ID": "Mezzanine Floors", "Risk": "Fall from heights", 1: "has fencing and rails (0.30)", 2: "has 2 means of access and regress (0.15)", 3: "has toe boards (0.27)", 4: "has greater than 7ft to the roof/next floor (0.15)", 5: "has adequate lighting (0.1)"},
    {"Row": 21, "HV": 5, "ID": "plaza or balconies", "Risk": "Fall from heights", 1: "fenced or guard rails (0.3)", 2: "height more than 6'6\" above ground or next floor (0.10)", 3: "wind velocity < 15 ft/min (0.3)", 4: "workers use this area regularly (0.10)", 5: "has alternate means of egress (0.15)"}
]

dataset_s3 = [
    {"Row": 1, "HV": 3, "ID": "solar /static / lightening", "Risk": "Soft tissue injury endocrine disruptors", 1: "awareness and information (0.13)", 2: "Exposure prevention procedure training (0.15)", 3: "prevention devices and mechanisms in place (0.20)", 4: "PPE & Protective equipment where necessary", 5: "surveillance and monitoring done (0.23)"},
    {"Row": 2, "HV": 2, "ID": "RADIATON Radiowaves", "Risk": "damage to retina and tissue", 1: "awareness and information (0.13)", 2: "Exposure prevention procedure training (0.15)", 3: "prevention devices and mechanisms in place (0.20)", 4: "PPE & Protective equipment where necessary (0.20)", 5: "surveillance and monitoring done (0.23)"},
    {"Row": 3, "HV": 4, "ID": "RADIATION - INFRARED LASERS", "Risk": "damage to retina and tissue &fire hazard", 1: "PPE - Eye protection and equipment (0.25)", 2: "surveillance and monitoring done (0.23)", 3: "operational procedure adhered to (0.20)", 4: "training and awareness certification (0.20)", 5: "awareness protocols for the emergency procedure (0.10)"},
    {"Row": 4, "HV": 3, "ID": "RADIATION Ultraviolet (UV)", "Risk": "Mutagenic, tissue damage, eye damage", 1: "awareness and training (0.20)", 2: "PPE for the eyes and skins provided (0.25)", 3: "surveillance and monitoring done (0.23)", 4: "procedural guidelines in place (0.20)", 5: "proper supervision in place (1.0)"},
    {"Row": 5, "HV": 2, "ID": "RADIATION Microwaves", "Risk": "cataracts, burns and cancer", 1: "awareness and information done (0.25)", 2: "ventilation for in microwave operation space (0.15)", 3: "operational procedure posted (0.33)", 4: "instructions for safe use of microwave posted (0.15)", 5: "device at least 3ft from persons (0.10)"},
    {"Row": 6, "HV": 4, "ID": "RADIATION X-Ray", "Risk": "Mutagenic", 1: "awareness and training (0.25)", 2: "personal monitoring device (0.33)", 3: "personal protective equipment in place (0.15)", 4: "adherence to exposure limits (0.17)", 5: "medical monitoring (0.8)"},
    {"Row": 7, "HV": 2, "ID": "EMF Radiation", "Risk": "suspected carcinogenic (leukemia)", 1: "awareness and training (0.25)", 2: "routers and connect stations located at least 10ft from workers (0.3)", 3: "Wiring and connect cable in sleeves or conduits away from floor (0.3)", 4: "monitoring and evaluation (0.1)", 5: ""},
    {"Row": 8, "HV": 5, "ID": "wiring Electrial", "Risk": "shocks and burns + Fire", 1: "wiring in sleeves or conduits (0.3)", 2: "plugs or connection points covered (0.27)", 3: "no wiring running across the floor (0.1)", 4: "no sparking switches or connect point (0.2)", 5: "no unattached exposed wire ends (0.1)"},
    {"Row": 9, "HV": 2, "ID": "Wiring; telephone and IT", "Risk": "STF", 1: "no wiring and cables running across the floor", 2: "no wiring hanging loosely from wall (0.21)", 3: "spider-webbed at workstation (0.25)", 4: "no bruised or damaged wiring (0.20)", 5: "hub poorly positioned"}
]

dataset_s4 = [
    {"Row": 1, "HV": 4, "ID": "Chemical storage", "Risk": "TOXIC EXPOSURE", 1: "storage in an approved cabinet or cupboard", 2: "access to storage area controlled (0.25)", 3: "storage according to classification (0.25)", 4: "cupboard storage area labeled (0.1)", 5: "chemical handling instructions seen (0.10)"},
    {"Row": 2, "HV": 2, "ID": "Chemical labeling", "Risk": "TOXIC EXPOSURE", 1: "GHS labels attached (0.2)", 2: "Appropriate language (0.2)", 3: "label legible (0.2)", 4: "GHS Chemical Symbol visible", 5: "GHS, CAS, EC OR UN number is on"},
    {"Row": 3, "HV": 4, "ID": "Chemical Registry Maintained", "Risk": "CONTROL", 1: "register maintained (0.23)", 2: "register entries up to date (0.27)", 3: "class of the chemical is shown in the register (0.25)", 4: "PPE requirements shown graphically (0.22)", 5: ""},
    {"Row": 4, "HV": 4, "ID": "MSDS for chemical used available", "Risk": "CONTROL", 1: "MSDS Kept in e/paper file (0.3)", 2: "MSDS Readily accessible (0.2)", 3: "all MSDS Documents from certified source", 4: "workers are aware of and use", 5: ""},
    {"Row": 5, "HV": 4, "ID": "Classified Critical Substance used", "Risk": "TOXIC EXPOSURE", 1: "there is clear procedure for handling these chemicals", 2: "workers are trained and sensitised to safety protocols (0.2)", 3: "spill response protocols and signage in place (0.18)", 4: "environmental monitoring and evaluation (0.17)", 5: "regulatory compliance and adherence (0.2)"},
    {"Row": 6, "HV": 4, "ID": "Classified Critical Substance Registry", "Risk": "TOXIC EXPOSURE", 1: "register readily accessible (0.23)", 2: "register entries up to date (0.20)", 3: "name of the person handling the chemical logged (0.21)", 4: "date and time of exposure shown (0.15)", 5: "medical surveillance for workers logged (0.18)"},
    {"Row": 7, "HV": 3, "ID": "Chemical Handling", "Risk": "TOXIC EXPOSURE", 1: "PPE for handling chemical by class", 2: "procedure for handling chemicals displayed (0.17)", 3: "workstation with suitable equipment provided", 4: "chemicals exposure is recorded", 5: "reactive chemicals kept apart (0.2)"},
    {"Row": 8, "HV": 5, "ID": "Asbestos / Hardwood Dust exp", "Risk": "CARCINOGENIC EXPOSURE", 1: "workers are trained and aware (0.2)", 2: "personal protective equipment provided (0.2)", 3: "local exhaust ventilation hoods provided (0.2)", 4: "dust mask / respirators regime in place", 5: "daily decontamination done (0.15)"},
    {"Row": 9, "HV": 5, "ID": "explosive / Flammable chemicals", "Risk": "fire and explosion", 1: "chemicals stored in appropriately labelled containers", 2: "stored in a fire / explosion protection area (0.20)", 3: "Protocol for using chemicals posted (0.17)", 4: "fire fighting equipment appropriately placed (0.2)", 5: "fire warning and appropriate exists provided (0.15)"},
    {"Row": 10, "HV": 4, "ID": "Heavy metals", "Risk": "Heavy Metal Poisoning, Toxicity", 1: "respirator / dust mask provided (0.23)", 2: "Other PPE Provided (0.17)", 3: "negative pressure changing area (0.25)", 4: "shower for change provided (0.20)", 5: "medical surveillance for workers logged (0.13)"},
    {"Row": 11, "HV": 3, "ID": "emergency Response", "Risk": "EMERGENCY RESPONSE", 1: "first aid (0.2)", 2: "emergency Eye Wash (0.2)", 3: "energ. Alarm (0.2)", 4: "fire extinguishers (0.17)", 5: "emerg exit (0.2)"},
    {"Row": 12, "HV": 2, "ID": "chemical waste disposal", "Risk": "CONTROL", 1: "Marked and seperate waste receptacles (0.23)", 2: "waste disposal by certified contactor (0.17)", 3: "training for treating with spills (0.17)", 4: "waste disposal done timely (0.20)", 5: "trenches in floor for sills (0.21)"}
]

dataset_s5 = [
    {"Row": 1, "HV": 3, "ID": "Insects; wasps, Hornets, Bees", "Risk": "venom", 1: "Large colony identified (-0.25)", 2: "Small colony seen (-0.2)", 3: "insects seen in the wkspace (-0.25)", 4: "control program in placem (0.35)", 5: "insects or nests not seen (0.61)"},
    {"Row": 2, "HV": 3, "ID": "Scorpions and centipedes", "Risk": "venom", 1: "many insects seen moving around (-0.25)", 2: "Small number of insects seen moving arround (-0.2)", 3: "insects seen in the wkspace (-0.25)", 4: "control program in place (0.35)", 5: "no insects seen (0.61)"},
    {"Row": 3, "HV": 4, "ID": "Rodents", "Risk": "leptospirocis", 1: "many rodents seen (-0.25)", 2: "few rodents seen (-0.2)", 3: "rodents seen in the wkspace (-0.25)", 4: "control program in place (0.35)", 5: "no rodents or droppings seen (0.61)"},
    {"Row": 4, "HV": 3, "ID": "Lice, ticks, flees", "Risk": "bites, lymes dieases or spotted fever", 1: "workers complain (-0.2)", 2: "workers have bites and marks (-0.25)", 3: "workers have rash (-0.23)", 4: "control program in place", 5: "no insects seen (0.61)"},
    {"Row": 5, "HV": 2, "ID": "roaches", "Risk": "infections", 1: "many insects seen moving around", 2: "Small number of insects seen", 3: "strange odour in the building", 4: "control program in place", 5: "no insects seen (0.61)"},
    {"Row": 6, "HV": 3, "ID": "Fungi", "Risk": "Allergies, Mycosis", 1: "high humidity damp coditions (-0.2)", 2: "fungal growth identified (-0.23)", 3: "persons are affected (infections) (-0.25)", 4: "control program in place (0.35)", 5: "no fungal growth seen (0.61)"},
    {"Row": 7, "HV": 3, "ID": "Moulds & Spores", "Risk": "Allergies mycosis", 1: "High humid, cool condition (-0.2)", 2: "visible mould growth (0.24)", 3: "persons report increase in repiratory illness (-0.26)", 4: "control program in place (0.35)", 5: "no mould seen (0.61)"},
    {"Row": 8, "HV": 2, "ID": "Termites", "Risk": "allergies", 1: "termite tracks seen (-0.2)", 2: "wood strucutre damage seen (-0.03)", 3: "insects sighted moving arround (-0.1)", 4: "control program in place (0.35)", 5: "no termites seen (0.61)"},
    {"Row": 9, "HV": 3, "ID": "PIGEONS", "Risk": "psittacosis, candidiasis or cryptococcosis-(Bacterial Infections)", 1: "pigeons seen nesting in the building (-0.2)", 2: "pigeons have access to the wkplace (-0.24)", 3: "pigeon droppings found on working areas (-0.3)", 4: "control program in place (0.35)", 5: "no pigeons seen (0.61)"},
    {"Row": 10, "HV": 3, "ID": "SHEEP & CATTLE", "Risk": "Bacterial infection-ANTHRAX", 1: "workers operate in sheep cattle pens (-0.25)", 2: "cases of nfections occured (-0.25)", 3: "shower and change after work policy inplace", 4: "no infected animals identified (0.25)", 5: "no cases of anthrax or infection seen (0.56)"},
    {"Row": 11, "HV": 3, "ID": "SOIL AND METAL", "Risk": "Bacterial infection - TETANUS", 1: "wokers handle soil and or metal (-0.3)", 2: "cases of tetanus infection occurred (-0.3)", 3: "hand washing station provided (0.13)", 4: "profalatic tetanus shots for workers", 5: "no cases of tetanus infection reported (0.56)"},
    {"Row": 12, "HV": 3, "ID": "FOOD PREPARATION", "Risk": "Bacterial infection - Salmonella", 1: "workers handle and prepare food (-0.3)", 2: "workers' hair and clothing covered. (0.15)", 3: "Meat prep done according to hygiene", 4: "works have food handlers permit", 5: "no cases of salmonellosis (0.36)"}
]

dataset_s6 = [
    {"Row": 1, "HV": 4, "ID": "workstation adaptability seating /standing", "Risk": "heart related disease METABOLIC SYNDROME", 1: "static work arrangement standing only (-0.6)", 2: "static work arrangement sitting only (-0.6)", 3: "walk less than 2000 steps per day (-0.3)", 4: "combination walking, sitting, standing > 2000 stps/day", 5: "combination sitting/walk >6000 steps per day (0.75)"},
    {"Row": 2, "HV": 4, "ID": "Workstation suitability, reach etc", "Risk": "DVT / RSI", 1: "stretching and reaching for objects on workstation (-0.2)", 2: "worker has ache in arms and neck (-0.25)", 3: "slot workstation (-0.25)", 4: "L workstation (0.15)", 5: "U Workstation (0.75)"},
    {"Row": 3, "HV": 3, "ID": "workstation - legroom", "Risk": "lower back ache and leg muscle fatigue", 1: "not able to stretch out legs under desk (-0.3)", 2: "workers stores personal objects under desk (-0.25)", 3: "equipment or work related gadgets under desk (-0.25)", 4: "files or paper stacked under desk (-0.17)", 5: "no foot rest under desk (-0.2)"},
    {"Row": 4, "HV": 3, "ID": "Workstation env.", "Risk": "Exhaustion Drowsiness", 1: "", 2: "", 3: "", 4: "", 5: ""},
    {"Row": 5, "HV": 3, "ID": "seating hand rest (HAR)", "Risk": "RSI", 1: "chair has no HR (-0.5)", 2: "HR cannot be adjusted (-0.3)", 3: "HR is damaged (-0.25)", 4: "worker is unsatisfied", 5: "worker is satisfied with HR (0.92)"},
    {"Row": 6, "HV": 3, "ID": "seating back support (BR)", "Risk": "Back Injury", 1: "Chair has no BR (-0.94)", 2: "BR Cannot be adjusted (-0.3)", 3: "BR is damaged (-0.25)", 4: "worker is unsatisfied", 5: "Worker is satisfied with BR (0.94)"},
    {"Row": 7, "HV": 3, "ID": "Standing all day at Work Station (WS)", "Risk": "RSI", 1: "Standing all day no seat provided", 2: "standing all day without a foot rest (-0.20)", 3: "standing but moving all day (-0.15)", 4: "Alternate standing and sitting (0.25)", 5: "worker is comfortable (0.73)"},
    {"Row": 8, "HV": 3, "ID": "bending, Stooping and stretching (BSS)", "Risk": "RSI", 1: "BSS Regularly (-0.7)", 2: "BSS from time to time (-0.05)", 3: "worker experience pain and discomfort", 4: "training and instructions to BSS (0.30)", 5: "equipment and devices provided to assist BSS"},
    {"Row": 9, "HV": 3, "ID": "pulling and pushing", "Risk": "RSI /MSD", 1: "pushing and pulling on level ground (-0.35)", 2: "pushing and pulling on incline (-0.55)", 3: "pushing or pulling reg. with mechanical lifting equipment (-0.35)", 4: "pushing or pulling heavy wt occasionally W mec.", 5: "no pushing or pulling required (0.90)"},
    {"Row": 10, "HV": 4, "ID": "Lifting and Handling", "Risk": "RSI", 1: "lifting and handling loads required (-0.15)", 2: "lifting and handling acting alone with < 40lbs (-0.45)", 3: "lifting and handling acting alone with > 40lbs (-0.65)", 4: "training and instructions on lifting and handling done (0.25)", 5: "NO L/H required (0.75)"},
    {"Row": 11, "HV": 3, "ID": "sedentary work", "Risk": "MSD", 1: "sitting for 8hr or > daily (-0.7)", 2: "sitting for >6hr & <8hr daily (-0.6)", 3: "sitting for >4hr & <6hrs daily (-0.46)", 4: "walking for more than > 4hr daily", 5: "walking / moving and occasionally sitting"}
]

dataset_s7 = [
    {"Row": 1, "HV": 4, "ID": "Floor Surface", "Risk": "Slips, Trips & Falls (STFs)", 1: "objects stacked on floor (-0.2)", 2: "wires or cables on floor (-0.2)", 3: "even non slip floor surface (0.45)", 4: "floor swept and cleaned (0.25)", 5: "walkways and spaces clear (0.27)"},
    {"Row": 2, "HV": 3, "ID": "House Keeping", "Risk": "Slips, Trips & Falls (STFs)", 1: "floors are swepted and swabbed", 2: "furniure and equipt dusted and swabbed", 3: "pest control program in place (0.2)", 4: "walls are painted and clean", 5: "structrue in good repair (0.17)"},
    {"Row": 3, "HV": 3, "ID": "Storage of equipt and tools", "Risk": "clutter and obstruction STF", 1: "storage provided in appropriate area (0.15)", 2: "storage area kept in clean clutter free way (0.25)", 3: "no junck or derelict equipment stored (0.13)", 4: "equipt. And tools storage labbled (0.2)", 5: "ladders and steps provided to reach eqipt/tools (0.2)"},
    {"Row": 4, "HV": 3, "ID": "Maintenance - Grounds & Building", "Risk": "Building related injuries", 1: "lawns, hedges and subry needs upkeep (-0.2)", 2: "walkways and footpath dirty and cracks (-0.2)", 3: "walls, doors and fixture in poor relpair (-0.2)", 4: "all buildings w/house or s/house in needs", 5: "perimeter fencing in good condition (-0.18)"},
    {"Row": 5, "HV": 4, "ID": "Walkway, passages fire escape & Aisles", "Risk": "STF /Fire escape", 1: "Emerg. escape route clearly marked (0.2)", 2: "passages and walkways free of obstacles (0.23)", 3: "properly lit walkways and passages (0.23)", 4: "free from odours or fumes (0.15)", 5: "signs and lables to indicate exits and entrances (0.15)"},
    {"Row": 6, "HV": 3, "ID": "Storage of fuels, flamable fluids, or chemicals", "Risk": "fire hazard. and STF hazard", 1: "certif. fuel tank in place (0.23)", 2: "fuel tank grounded (0.21)", 3: "safety parameter fincing around tank (0.13)", 4: "fire proof storage room provided (0.20)", 5: "electrical fittings and swithces spark proof (0.20)"},
    {"Row": 7, "HV": 3, "ID": "Sanitation environmental health", "Risk": "Public Health nuisance", 1: "garbage stored in secured and acceable space", 2: "garbage in seperated receptacle (0.15)", 3: "pest have no access to garbage (0.26)", 4: "no, odors emanating from garabge site", 5: "appropriate waste removal (0.17)"},
    {"Row": 8, "HV": 5, "ID": "Stairways / Steps Slopes", "Risk": "STF", 1: "threads are in good conditions", 2: "hand rails provide on both side", 3: "hand reails on one side only", 4: "no rugs cover on threads", 5: "no metal strips on thread edge"},
    {"Row": 9, "HV": 4, "ID": "Driveways and approaches", "Risk": "STF", 1: "smooth non slip surface (0.25)", 2: "no pothole or cracks in surface (0.20)", 3: "pedestrian protected from vehicular traffic (0.15)", 4: "marked for traffic regulation (0.12)", 5: "is not a traffic hazard because of position"},
    {"Row": 10, "HV": 2, "ID": "Windows & Skylight", "Risk": "psychosocial R", 1: "windowless office (-0.85)", 2: "fixed windows (-0.14)", 3: "windows can be opened (0.15)", 4: "window or skylight within 15ft of every worker (0.35)", 5: "window has blinds or light control (0.45)"},
    {"Row": 11, "HV": 3, "ID": "Egress and Accesses (E/A)", "Risk": "allows for emergency exit of the building", 1: "At least 2 means of access/egress to the building", 2: "Emergency Exit clearly marked (0.17)", 3: "emergency exits swing outward (0.25)", 4: "Emergency E/A equipped with security locks (0.20)", 5: "Emergency Exit clear of obstacles (0.15)"},
    {"Row": 12, "HV": 3, "ID": "Building safety features Design and layout", "Risk": "allows for emergency exit of the building", 1: "has wheel chair access ramps/doors (0.2)", 2: "emergency escape route clearly marked and known (0.3)", 3: "elevators, lifts, and hoists have emergency warning devices", 4: "has an emergency warning device that can be heard in the building", 5: "all room exit to common area (0.13)"}
]

dataset_s8 = [
    {"Row": 1, "HV": 4, "ID": "Tobacco Use & Second Hand Smoke", "Risk": "Carcinogenic and second hand smoke", 1: "Tobacco use prevention policy in place (0.23)", 2: "designated tobacco use area assigned (0.18)", 3: "sensitization and awareness of tobacco hazards (0.22)", 4: "tobacco use prevention policy has sanction for breach (0.17)", 5: "no smoking signs and notice in sensitive places (0.17)"},
    {"Row": 2, "HV": 3, "ID": "Alcohol & Drugs", "Risk": "Intoxication & health impairment", 1: "alcohol and drugs use prevention policy", 2: "awareness and use prevention in place (0.20)", 3: "sanction in place for breach (0.15)", 4: "HR Confidential report portal (0.17)", 5: "support system for users in place (0.20)"},
    {"Row": 3, "HV": 3, "ID": "HIVAIDS Workplace policy", "Risk": "Stigma and Discrimination", 1: "HIV AIDS Policy in place (0.23)", 2: "awareness and discrimination training (0.2)", 3: "sanction in place for breach (0.15)", 4: "HR Confidential report portal (0.17)", 5: "support system for affected persons in place (0.2)"},
    {"Row": 4, "HV": 2, "ID": "Rewards and recognition", "Risk": "lack of organizational loyalty", 1: "there is an annual awards programme (0.21)", 2: "workers are aware of the programme and how awarded (0.10)", 3: "personal and individual performance targets set (0.24)", 4: "awards recognition include social and technical aspects (0.24)", 5: "all categories of workers are included (0.30)"},
    {"Row": 5, "HV": 2, "ID": "work schedule Hours of Work", "Risk": "Mental health and Stress", 1: "workers Leave regularly deferred (0.1)", 2: "regular overtime = to, or exceeding 4 hrs/day (0.1)", 3: "overtime scheduled as needed (0.24)", 4: "Granted emergency and time off as needed", 5: "standard 40 hr work week (0.3)"},
    {"Row": 6, "HV": 3, "ID": "healthy sleep routine", "Risk": "Focus and mental acuity", 1: "equipment operators having nerve-related rest issues (-0.45)", 2: "on call at nights, fluctuating sleep time (-0.25)", 3: "work hrs allow for < 6 hrs /night regularly (0.15)", 4: "work hrs allow for regularly >6 & <8 hrs / night", 5: "work hrs allow for regularly 8 or more hrs/night (0.85)"},
    {"Row": 7, "HV": 4, "ID": "Rest and recuperation", "Risk": "Burnout", 1: "more than 1 hr work breaks given/day (0.2)", 2: "lunch break more than 30 mins (0.1)", 3: "at least 1 coffee break given in 8hr work shift (0.1)", 4: "workplace recreational activities in place (0.25)", 5: "Granted scheduled and adhoc leave as needed (0.31)"},
    {"Row": 8, "HV": 4, "ID": "Violence prevention", "Risk": "Physical and emotional injuries", 1: "violence prevention policy in place", 2: "awareness and prevention strategy in place (0.23)", 3: "support system for affected workers in place (0.23)", 4: "HR Confidential report portal in place (0.15)", 5: "fair discipline and disciplinary action in place for breach"},
    {"Row": 9, "HV": 4, "ID": "Discrimination and stigma", "Risk": "Anxiety and depression", 1: "gender equal opportunity employment policy in place (0.23)", 2: "address and fraternity identity removed from employment consideration (0.15)", 3: "HR Employment Committee in place (0.17)", 4: "HR Confidential report portal to report D&S in place", 5: "D&S grievance handling mechanism in place (0.22)"},
    {"Row": 10, "HV": 4, "ID": "BUTO HR Practices", "Risk": "Depression and mental health issues", 1: "Coercion forcing and compelling persons to action", 2: "threats from supervisors or coworkers (-0.18)", 3: "expressing Aggression and anger in dealing with coworker", 4: "HR Confidential report portal (0.43)", 5: "grievance handling process in place (0.43)"},
    {"Row": 11, "HV": 4, "ID": "Sexual harassment", "Risk": "Anxiety, depression and mental health issues", 1: "Employees are informed that harassment is prohibited", 2: "sexual harassment policy in place (0.23)", 3: "workers are aware of harassment behavior (0.23)", 4: "HR Confidential report portal (0.17)", 5: "grievance handling policy in place (0.15)"},
    {"Row": 12, "HV": 3, "ID": "Location Anxiety", "Risk": "Anxiety and emotional distress, sleep disorder, low energy", 1: "workplace located in violence prone area (-0.25)", 2: "workplace located in adverse environmental conditions (-0.25)", 3: "workplace location in isolated location (-0.18)", 4: "workplace located in a safe and accessible location", 5: "safe transportation to and from the worksite in place (0.25)"},
    {"Row": 13, "HV": 4, "ID": "Work demand stress", "Risk": "Stress, anxiety and burnout", 1: "performance targets are reasonable and attainable", 2: "low intensity physical activity (0.14)", 3: "Objectives are attainable with supervisor support (0.15)", 4: "Meeting targets is challenging but attainable", 5: "workers satisfied with performance assessment (0.16)"},
    {"Row": 14, "HV": 4, "ID": "Job Security", "Risk": "wellbeing", 1: "economic insecurity (low wage rates) (-0.18)", 2: "contract work (-0.22)", 3: "can be easily dismissed without due process (-0.18)", 4: "no involvement in making decision about work (-0.20)", 5: "uncertainty about continuation of job (-0.20)"},
    {"Row": 15, "HV": 2, "ID": "Nutrition", "Risk": "reduced productivity, fatigue, poor mental focus", 1: "planned healthy meals provided", 2: "health related specially prepared meals (0.2)", 3: "Adherence to meal time while at work (0.21)", 4: "affordable nutritious meals available", 5: "lunchroom canteen provided on site (0.2)"},
    {"Row": 16, "HV": 3, "ID": "isolated Remote Work", "Risk": "Stress and burnout", 1: "remote work routinely (-0.6)", 2: "remote work occasionally (-0.4)", 3: "lack of social contact on location (-0.15)", 4: "lack of administrative support (-0.15)", 5: "no emergency response support (-0.15)"}
]

dataset_s9 = [
    {"Row": 1, "HV": 3, "ID": "Place For Taking Meals", "Risk": "wellbeing", 1: "none provided. Req. (-0.70)", 2: "capacity for seating meet req. (0.25)", 3: "lunch area sanitary and clean (0.27)", 4: "ventilation Meets req. (0.23)", 5: "has appropriate waste disposal"},
    {"Row": 2, "HV": 3, "ID": "Drinking Water", "Risk": "wellbeing", 1: "none provided (-0.70)", 2: "tap water only provided (0.20)", 3: "filtered and treated water (0.36)", 4: "accessible to all workers (0.44)", 5: "utensils and accommodation for access"},
    {"Row": 3, "HV": 3, "ID": "Hand Washing Facility", "Risk": "wellbeing", 1: "none provided (-0.70)", 2: "taps are functional (no leaks) (0.20)", 3: "clean and sanitary conditions (0.30)", 4: "soap and hand drying provision provided", 5: "has appropriate waste disposal (0.21)"},
    {"Row": 4, "HV": 3, "ID": "Toilets for males and females", "Risk": "wellbeing", 1: "unisex provision only (-0.20)", 2: "separate male and female facilities (0.20)", 3: "clean and sanitary conditions (0.30)", 4: "functional (no leaks) (0.20)", 5: "appropriately ventilated (0.27)"},
    {"Row": 5, "HV": 3, "ID": "Restrooms for females", "Risk": "wellbeing", 1: "none provided (-0.70)", 2: "has a bed for resting (0.20)", 3: "bed has a privacy screen (0.40)", 4: "has water and utensil (0.26)", 5: "is supervised when in use (0.12)"},
    {"Row": 6, "HV": 3, "ID": "toilets and handwashing facilites for the physical disabled", "Risk": "enabling", 1: "not provided (-0.6)", 2: "bathroom satisfy legal req (0.32)", 3: "toilet stall has hand rails and assistant bars (0.28)", 4: "toilet doors swing both ways (0.20)", 5: "is equipped with hygiene requirements (0.17)"},
    {"Row": 7, "HV": 2, "ID": "Sanitizing stations", "Risk": "wellbeing", 1: "none provided (-0.45)", 2: "provided (0.72)", 3: "conspicuously displayed (0.23)", 4: "", 5: ""},
    {"Row": 8, "HV": 4, "ID": "ramps and access points for the physically disabled", "Risk": "enabling", 1: "none provided (-0.68)", 2: "provided meets legal requirement (0.25)", 3: "identified and suitable marked (0.24)", 4: "leads to entrance / exit that has assist mechanism", 5: "access to parking (0.17)"}
]

dataset_s10 = [
    {"Row": 1, "HV": 4, "ID": "PPE", "Risk": "SAFETY", 1: "provided (0.22)", 2: "inadequate (-0.20)", 3: "in good condition (0.24)", 4: "satisfy's legal req (0.30)", 5: "rules for wearing implemented (0.21)"},
    {"Row": 2, "HV": 3, "ID": "First Aid", "Risk": "Emergency Response", 1: "provided (0.23)", 2: "inadequate (-0.20)", 3: "needs reload (0.24)", 4: "satisfy's legal req", 5: "Best Practice (0.21)"},
    {"Row": 3, "HV": 3, "ID": "Trained First aider", "Risk": "Emergency Response", 1: "Inplace (0.27)", 2: "untrained first aider (-0.2)", 3: "trained first aider Certified (0.47)", 4: "trained first aider Nurse", 5: "trained first aider Doctor (0.68)"},
    {"Row": 4, "HV": 3, "ID": "Emergency warders (10 or > employees)", "Risk": "Emergency Response", 1: "warders are commissioned (0.27)", 2: "warders untrained (-0.2)", 3: "warders have basic training (30)", 4: "warders are Equipped (0.13)", 5: "Warders have a managed assembly point (0.28)"},
    {"Row": 5, "HV": 4, "ID": "Safety personnel", "Risk": "SAFETY", 1: "safety officer or safety committee Inplace (0.27)", 2: "no OSH Personnel or committee in place (-0.30)", 3: "contact information of the committee or personnel posted (0.25)", 4: "OSH Committee or personnel Equipped (0.15)", 5: "OSH policy in place (0.31)"},
    {"Row": 6, "HV": 3, "ID": "Safety Sensitization of the workplace", "Risk": "SAFETY", 1: "done routinely (0.21)", 2: "sanitization not done routinely (-0.35)", 3: "sanitization team trained and competent (0.35)", 4: "hygiene protocol Is implemented in high-contact", 5: "done according to sanitization standard (0.25)"},
    {"Row": 7, "HV": 3, "ID": "Safety Communication", "Risk": "SAFETY", 1: "Inplace, signs and communique (0.27)", 2: "presentations or talks on safety done (0.2)", 3: "staff are briefed on online discussions (0.2)", 4: "Staff are aware thru' social media tips", 5: "booklet, safety literature circulated (0.15)"},
    {"Row": 8, "HV": 3, "ID": "emergency evacuation procedure", "Risk": "Emergency Response", 1: "established (0.25)", 2: "staff sensitised to the drill (0.2)", 3: "timing established to totally evacuate building (0.1)", 4: "assembly points identified (0.2)", 5: "emergency service equipment available (0.21)"},
    {"Row": 9, "HV": 3, "ID": "Health Promotion", "Risk": "SAFETY", 1: "done (0.27)", 2: "by presentations (0.3)", 3: "posters or pamphlets (0.2)", 4: "videos and clips (0.2)", 5: "promotional booklets (0.2)"},
    {"Row": 10, "HV": 3, "ID": "OSH Committee", "Risk": "SAFETY", 1: "Inplace (0.27)", 2: "has reps from workers and management (0.2)", 3: "meets and deliberates (0.18)", 4: "composition and number meets legal req.", 5: "committ. Is a part of management structure (0.18)"}
]

# Top Overall Banner
st.markdown('<div class="banner">PLEASE SELECT ALL THAT IS APPLICABLE</div>', unsafe_allow_html=True)

# Selection Tracking
selected_data = []

# Helper render function for standard hazard tables with individual section download
def render_section(title, css_class, dataset, section_name, is_pink_risk=False, custom_mit_title="MITIGATION"):
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section Header Row with Individual Download Button
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown(f'<div class="{css_class}">{title}</div>', unsafe_allow_html=True)
    
    section_rows = []
    
    # Render Hazard & Mitigation Table Headers
    col_meta1, col_meta2, col_meta3 = st.columns([1, 4, 15])
    with col_meta2:
        st.markdown('<div class="table-header bg-light-blue">HAZARD</div>', unsafe_allow_html=True)
    with col_meta3:
        st.markdown(f'<div class="table-header bg-light-blue">{custom_mit_title}</div>', unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7, col_h8, col_h9 = st.columns([0.5, 0.7, 2.5, 2.0, 2.4, 2.4, 2.4, 2.4, 2.4])
    col_h1.markdown('<div class="table-header bg-light-blue">#</div>', unsafe_allow_html=True)
    col_h2.markdown('<div class="table-header bg-light-blue">H/V</div>', unsafe_allow_html=True)
    col_h3.markdown('<div class="table-header bg-light-blue">ID</div>', unsafe_allow_html=True)
    col_h4.markdown('<div class="table-header bg-light-blue">RISK</div>', unsafe_allow_html=True)
    col_h5.markdown('<div class="table-header bg-light-blue">1</div>', unsafe_allow_html=True)
    col_h6.markdown('<div class="table-header bg-light-blue">2</div>', unsafe_allow_html=True)
    col_h7.markdown('<div class="table-header bg-light-blue">3</div>', unsafe_allow_html=True)
    col_h8.markdown('<div class="table-header bg-light-blue">4</div>', unsafe_allow_html=True)
    col_h9.markdown('<div class="table-header bg-light-blue">5</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin: 4px 0px;'>", unsafe_allow_html=True)

    risk_bg = "#FF69B4" if is_pink_risk else "#00B0F0"

    for item in dataset:
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.5, 0.7, 2.5, 2.0, 2.4, 2.4, 2.4, 2.4, 2.4])
        
        c1.write(f"**{item['Row']}**")
        c2.markdown(f"<div style='text-align:center; font-weight:bold; color:#D9822B;'>{item['HV']}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='background-color:#FF0000; color:white; padding:6px; font-weight:bold;'>{item['ID']}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='background-color:{risk_bg}; color:black; padding:6px; font-weight:bold;'>{item['Risk']}</div>", unsafe_allow_html=True)
        
        cols = [c5, c6, c7, c8, c9]
        selected_levels = []
        
        for level_num in range(1, 6):
            raw_val = item[level_num]
            clean_val = clean_text(raw_val)
            
            if clean_val:
                is_selected = cols[level_num - 1].checkbox(
                    label=clean_val,
                    key=f"check_{section_name.lower().replace(' ', '')}_r{item['Row']}_l{level_num}"
                )
                if is_selected:
                    selected_levels.append(level_num)
            else:
                cols[level_num - 1].write("-")
                
        row_entry = {
            "Section": section_name,
            "Row": item["Row"],
            "Hazard ID": item["ID"],
            "Risk": item["Risk"],
            "Base H/V": item["HV"],
            "Selected Levels": selected_levels
        }
        selected_data.append(row_entry)
        section_rows.append(row_entry)
        
    # Section level download button
    with col_t2:
        sec_df = pd.DataFrame(section_rows)
        sec_csv = sec_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {section_name}",
            data=sec_csv,
            file_name=f"{section_name.lower().replace(' ', '_')}_report.csv",
            mime="text/csv",
            key=f"btn_dl_{section_name.lower().replace(' ', '')}"
        )

# Render Sections 1 to 9
render_section("SECTION 1 - WORK ENVIRONMENT", "section-title-s1", dataset_s1, "SECTION 1")
render_section("SECTION 2 - GENERAL SAFETY", "section-title-s2", dataset_s2, "SECTION 2")
render_section("SECTION 3 - RADIATION & ENERGY", "section-title-s3", dataset_s3, "SECTION 3")
render_section("SECTION 4 - CHEMICALS & HAZARDOUS SUBSTANCES", "section-title-s4", dataset_s4, "SECTION 4")
render_section("SECTION 5 - BIOLOGICAL AGENTS", "section-title-s5", dataset_s5, "SECTION 5", custom_mit_title="HAZARD CONDITION")
render_section("SECTION 6 - ERGONOMICS", "section-title-s6", dataset_s6, "SECTION 6", custom_mit_title="HAZARD CONDITION")
render_section("SECTION 7 - WORKING CONDITION", "section-title-s7", dataset_s7, "SECTION 7")
render_section("SECTION 8 - PSYCHOSOCIAL", "section-title-s8", dataset_s8, "SECTION 8")
render_section("SECTION 9 - WELFARE", "section-title-s9", dataset_s9, "SECTION 9", is_pink_risk=True, custom_mit_title="HAZARD CONDITION")

# ==========================================
# RENDER SECTION 10 - SAFETY PREPAREDNESS
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.markdown('<div class="section-title-s10">SECTION 10 - SAFETY PREPAREDNESS</div>', unsafe_allow_html=True)

sec10_rows = []

col_meta1, col_meta2, col_meta3 = st.columns([1, 4, 15])
with col_meta2:
    st.markdown('<div class="table-header bg-light-blue">REQUIREMENT</div>', unsafe_allow_html=True)
with col_meta3:
    st.markdown('<div class="table-header bg-light-blue">PROVISION</div>', unsafe_allow_html=True)

col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7, col_h8, col_h9 = st.columns([0.5, 0.7, 2.5, 2.0, 2.4, 2.4, 2.4, 2.4, 2.4])
col_h1.markdown('<div class="table-header bg-light-blue">#</div>', unsafe_allow_html=True)
col_h2.markdown('<div class="table-header bg-light-blue">HVAL UE</div>', unsafe_allow_html=True)
col_h3.markdown('<div class="table-header bg-light-blue">ID</div>', unsafe_allow_html=True)
col_h4.markdown('<div class="table-header bg-light-blue">RISK</div>', unsafe_allow_html=True)
col_h5.markdown('<div class="table-header bg-light-blue">STATUS</div>', unsafe_allow_html=True)
col_h6.markdown('<div class="table-header bg-light-blue">1</div>', unsafe_allow_html=True)
col_h7.markdown('<div class="table-header bg-light-blue">2</div>', unsafe_allow_html=True)
col_h8.markdown('<div class="table-header bg-light-blue">3</div>', unsafe_allow_html=True)
col_h9.markdown('<div class="table-header bg-light-blue">4</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin: 4px 0px;'>", unsafe_allow_html=True)

for item in dataset_s10:
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.5, 0.7, 2.5, 2.0, 2.4, 2.4, 2.4, 2.4, 2.4])
    
    c1.write(f"**{item['Row']}**")
    c2.markdown(f"<div style='text-align:center; font-weight:bold; color:#D9822B;'>{item['HV']}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='background-color:#FF0000; color:white; padding:6px; font-weight:bold;'>{item['ID']}</div>", unsafe_allow_html=True)
    c4.markdown(f"<div style='background-color:#FF69B4; color:black; padding:6px; font-weight:bold;'>{item['Risk']}</div>", unsafe_allow_html=True)
    
    cols = [c5, c6, c7, c8, c9]
    selected_levels = []
    
    for level_num in range(1, 6):
        raw_val = item[level_num]
        clean_val = clean_text(raw_val)
        
        if clean_val:
            is_selected = cols[level_num - 1].checkbox(
                label=clean_val,
                key=f"check_s10_r{item['Row']}_l{level_num}"
            )
            if is_selected:
                selected_levels.append(level_num)
        else:
            cols[level_num - 1].write("-")
            
    row_entry = {
        "Section": "SECTION 10",
        "Row": item["Row"],
        "Requirement ID": item["ID"],
        "Risk": item["Risk"],
        "Base H/V": item["HV"],
        "Selected Levels": selected_levels
    }
    selected_data.append(row_entry)
    sec10_rows.append(row_entry)

with col_t2:
    sec10_df = pd.DataFrame(sec10_rows)
    sec10_csv = sec10_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download SECTION 10",
        data=sec10_csv,
        file_name="section_10_report.csv",
        mime="text/csv",
        key="btn_dl_s10"
    )

# Overall Summary Report
st.markdown("---")
st.subheader("📋 Complete Master Assessment Report")
summary_df = pd.DataFrame(selected_data)
st.dataframe(summary_df, use_container_width=True)

csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Complete Assessment Report (All Sections CSV)",
    data=csv,
    file_name="complete_workplace_risk_assessment_report.csv",
    mime="text/csv"
)
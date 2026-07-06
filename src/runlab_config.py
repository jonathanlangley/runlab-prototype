APP_MODES = ["Try demo scenarios", "Upload your own data", "Strava Sync (Coming Soon)"]

# Bump when limiter rules, thresholds, or scoring logic change materially.
ENGINE_VERSION = "1.0.0"

VALID_BETA_CODES = {"RUNLAB-BETA1"}
BETA_SIGNUP_URL = "https://runlab.ai/#beta"

DEMO_FILES = {
    "Baseline runner (mixed stimulus)": "data/sample_runs.csv",
    "Near-optimal but plateauing": "data/near_optimal_but_plateauing.csv",
    "Consistent plateau": "data/consistent_plateau.csv",
    "Inconsistent training": "data/inconsistent_training.csv",
    "High volume, low quality": "data/high_volume_no_quality.csv",
    "Too much intensity": "data/too_much_intensity.csv",
    "Declining load": "data/declining_load.csv",
}

DEMO_DESCRIPTIONS = {
    "Baseline runner (mixed stimulus)": "A typical mixed pattern with no single obvious disaster, useful for seeing the full report flow.",
    "Near-optimal but plateauing": "A strong pattern that may need one clearer progression signal.",
    "Consistent plateau": "Good rhythm, but several training levers have become static.",
    "Inconsistent training": "Irregular frequency and gaps between runs.",
    "High volume, low quality": "Good mileage, but limited structured quality.",
    "Too much intensity": "Hard work appears before the aerobic support is strong enough.",
    "Declining load": "Good consistency and moderate volume, but recent load has dropped.",
}

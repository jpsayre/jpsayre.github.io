const PROJECTS = {
    data: [
        {
            title: "Solar Intel",
            url: "https://getsolarintel.com",
            image: "",
            description: "A lead-generation platform that ranks residential properties by their likelihood of installing solar in the next 12 months. The system ingests parcel data, municipal permit records, Google Sunroof roof geometry, Census demographics, and economic indicators to produce ranked lists of high-probability homes for solar installers.",
            details: "The core pipeline runs 11 stages — from data ingestion and permit classification through walk-forward machine learning validation using an ensemble of models (LASSO, Random Forest, Gradient Boosting, LightGBM, Neural Net, and a Stacked Ensemble). Currently live for Boulder County, CO with San Diego, CA in progress. The customer-facing app is built with Next.js 14 and Supabase, featuring an interactive map explorer, home detail views, and a follow/alerts system for tracking properties.",
            tech: ["Python", "Next.js 14 + Supabase", "Google Sunroof API, Census ACS, Regrid", "scikit-learn, LightGBM"],
        },
    ],
    engineering: [],
    design: [
        {
            title: "Headphones",
            image: "assets/projects/design/Headphones.png",
            description: "",
            details: "",
            tech: [],
        },
        {
            title: "3D Modeling",
            image: "assets/projects/design/modeling.png",
            description: "",
            details: "",
            tech: [],
        },
        {
            title: "Guitar",
            image: "assets/projects/design/guitar.png",
            description: "",
            details: "",
            tech: [],
        },
    ],
};

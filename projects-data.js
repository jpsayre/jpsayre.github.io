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
        {
            title: "Predictive Component Failure Analysis",
            image: "",
            description: "Georgia Tech capstone project sponsored by Caterpillar. Built a predictive analytics system to identify heavy equipment likely to experience major component failures (hydraulic, engine, and transmission) before they occurred. The goal was to enable proactive maintenance, reducing unplanned downtime and costs.",
            details: "Aggregated multiple data sources — telematics events, oil sampling lab results, work order history, daily machine summaries, and operational metrics — into 30-day grouped feature sets per machine. Explored supervised learning approaches (logistic regression, decision trees) and unsupervised clustering techniques (K-Means, Mean Shift, Agglomerative). Clustering proved most effective at surfacing failure patterns given the limited labeled failure data. Also developed a Mean Time Between Failure model and built custom data pipelines to pull and merge data from SQL Server and Teradata cloud databases.",
            tech: ["Python", "SQL (SQL Server, Teradata)", "R / Radiant", "Tableau", "Logistic Regression, Decision Trees, K-Means, Mean Shift, Agglomerative Clustering"],
        },
    ],
    engineering: [],
    design: [
        {
            title: "3D Printed Headphones",
            image: "assets/projects/design/Headphones.png",
            description: "My original idea with this project was to make a small business selling custom designed premium headphones. There were a lot of fun challenges to overcome in making the prototype. The first was the design, I designed everything in Solidworks with the goal of minimizing parts, making them manufacturable, and aesthetically pleasing. To really differentiate them, I chose to make the headband out of bent walnut. This was in and of itself a huge challenge, as I had to learn how to steam wood and build the tooling to allow me to do that. A lot of trial and error, different woods, different thicknesses, but it eventually worked. But of course, unpadded wood isn't the most comfortable material to have on your head all day. So I experimented with padding options. I tried glueing cork to the wood, as well as different padding materials. But none both stayed put and were comfortable. I ended up implementing a solution of adding a leather strap that hung just below the wood. This was both comfortable and added to the premium materials feel of the product. My manufacturing plan was to first 3D print the parts, and then to cast them and create each new copy with a resin mold. This worked fairly well, but forced me to really think through the design. A huge challenge with resins is eliminating air-bubbles in them. So I did a lot of work to have no small features in the parts that would trap air, and then I experimented with vacuum techniques for the process itself. I was eventually able to get it working fairly well. For the speakers (drivers) I went on Alibaba and ordered a half dozen different kinds until I found the model that sounded the best. I sized the headphones accordingly. I also ordered premium headphone wires, and ear cushions to complete the look and feel. There were a lot of great design challenges to work through in creating these, and a lot of clever little solutions that were fun to think through. I ultimately didn't end up making a business out of it, as they were very time consuming to make and would not have scaled, but it was a fun project nonetheless.",
            details: "",
            tech: ["Solidworks","3D Printing","Resins","Headphone Drivers","Woodworking"],
        },
        {
            title: "3D Modeling",
            image: "assets/projects/design/modeling.png",
            description: "This is just a demonstration of some of the parts I've modeled in Solidworks. Most of my engineering experience with modeling was focused on large assemblies, hydraulic components, sheetmetal, machined parts, harness assemblies, and cabling using ProEngineer/Creo.",
            details: "",
            tech: ["Solidworks"],
        },
        {
            title: "Guitar",
            image: "assets/projects/design/guitar.png",
            description: "I had a moment of inspiration while playing golf. I set my bag down and the stand just opened. I wondered why this mechanism had never been implemented for a guitar case, as that would also be very convenient to have a stand on the go. I bought a cheap golf bag and took the stand off of it. I riveted onto a guitar bag and then I designed and 3D printed stand for the guitar. This both had the pegs to support the guitar, but also the mechanism that the stand pedal of the golf stand needs to deploy the legs. I incorporated all of this into the guitar bag and it worked very well. When the bag is set down, the stand deploys, when picked up it folds up against the bag.",
            details: "",
            tech: ["3D Printing"],
        },
    ],
};

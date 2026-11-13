
import fs from "node:fs";

const username = "Mano522";
const token = process.env.GH_TOKEN;

if (!token) {
  throw new Error("GH_TOKEN is missing");
}

const year = new Date().getUTCFullYear();

const query = `
query {
  user(login: "${username}") {
    contributionsCollection(
      from: "${year}-01-01T00:00:00Z"
      to: "${year + 1}-01-01T00:00:00Z"
    ) {
      totalCommitContributions
    }
  }
}`;

const response = await fetch(
  "https://api.github.com/graphql",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query })
  }
);

const result = await response.json();

if (!response.ok || result.errors) {
  throw new Error(
    JSON.stringify(result.errors || result)
  );
}

const commits =
  result.data.user.contributionsCollection
    .totalCommitContributions;

// Car grows with contributions.
const scale = Math.min(
  1.3,
  0.38 + commits / 1500
);

const svg = `
<svg xmlns="http://www.w3.org/2000/svg"
     width="1000" height="210"
     viewBox="0 0 1000 210">

  <rect width="1000" height="210"
        rx="16" fill="#101827"/>

  <text x="500" y="30"
        text-anchor="middle"
        fill="#39D353"
        font-size="19"
        font-weight="bold">
    MANOJ'S GITHUB JOURNEY
  </text>

  <text x="500" y="55"
        text-anchor="middle"
        fill="white" font-size="15">
    ${commits} commits in ${year}
  </text>

  <path d="M0 155 H1000"
        stroke="#64748b" stroke-width="5"/>

  <path d="M0 180 H1000"
        stroke="white" stroke-width="3"
        stroke-dasharray="35 25">
    <animate attributeName="stroke-dashoffset"
      from="0" to="-120"
      dur="1s" repeatCount="indefinite"/>
  </path>

  <g>
    <animateTransform
      attributeName="transform"
      type="translate"
      values="-400 0;1100 0"
      dur="9s"
      repeatCount="indefinite"/>

    <g transform="scale(${scale})">

      <!-- Innova Crysta body -->
      <path d="M18 145 L28 105
        Q35 91 60 88 L85 45
        Q95 30 120 30 L260 30
        Q278 30 290 49 L325 90
        Q348 95 354 120 L355 145 Z"
        fill="#e2e8f0"
        stroke="#94a3b8" stroke-width="3"/>

      <!-- Windows -->
      <path d="M91 85 L112 43
        L165 43 L165 85 Z"
        fill="#18334c"/>

      <path d="M174 43 L254 43
        L285 85 L174 85 Z"
        fill="#18334c"/>

      <!-- Front grille -->
      <path d="M330 108 L349 113
        L350 133 L330 133 Z"
        fill="#334155"/>

      <!-- Lights -->
      <rect x="345" y="95" width="12"
        height="13" rx="3" fill="#fff7ae"/>

      <rect x="20" y="105" width="9"
        height="20" fill="#ef4444"/>

      <!-- Wheels -->
      <g fill="#111827"
         stroke="#94a3b8" stroke-width="4">
        <circle cx="92" cy="143" r="24"/>
        <circle cx="292" cy="143" r="24"/>
      </g>

      <g fill="#cbd5e1">
        <circle cx="92" cy="143" r="10"/>
        <circle cx="292" cy="143" r="10"/>
      </g>

    </g>
  </g>
</svg>`;

fs.mkdirSync("assets", { recursive: true });

fs.writeFileSync(
  "assets/innova-contribution-car.svg",
  svg
);

console.log(
  `Innova generated with ${commits} commits`
);

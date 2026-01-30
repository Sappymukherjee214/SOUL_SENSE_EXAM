# 🌐 Soul Sense Web Frontend

A modern Next.js 14 dashboard for the Soul Sense EQ Test platform.

---

## 🚀 Getting Started

### 1. Installation

```bash
backend: 

cd backend/fastapi
python start_server.py --y

frontend:

cd frontend-web
npm install
npm run dev

```

### 2. Development

```bash
npm run dev
```

👉 Open [http://localhost:3005](http://localhost:3005)

> [!IMPORTANT]
> **Backend Required**: Ensure the FastAPI server is running on port 8000 for data fetching to work.
>
> ```bash
> python backend/fastapi/start_server.py
> ```

---

## 🏗️ Architecture

This project follows **Domain-Driven, Feature-Sliced** architecture.

- **Components**: UI primitives in `/ui`, layout in `/layout`, sections in `/sections`.
- **Standards**: Absolute imports (`@/`), strict architectural boundaries, and barrel files.
- **Reference**: See [ADR 001: Frontend Architecture](../docs/architecture/001-frontend-structure.md) for full details.

---

## 🛠️ Tech Stack

- **Core**: Next.js 14 (App Router), React 18, TypeScript
- **Style**: Tailwind CSS, Framer Motion (Animations)
- **UI**: Radix UI, Lucide Icons, Recharts (Data Viz)
- **Logic**: Zod + React Hook Form, Recharts

---

## ✅ Quality Gates

Before pushing, ensure:

- `npm run lint` - Code style & architecture check
- `npm run build` - Production build verification

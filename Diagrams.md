# Project Diagrams

## DFD-0 (System Context)

```mermaid
flowchart TD
  User["User"]
  System["Course Platform"]
  DB["Database"]
  AI["AI Service"]
  YT["YouTube API"]
  IMG["Image Generation API"]

  User -- Interacts --> System
  System -- Stores/Retrieves --> DB
  System -- Sends Prompts --> AI
  System -- Gets Videos --> YT
  System -- Gets Images --> IMG
```

## DFD-1 (Major Modules)

```mermaid
flowchart TD
  User["User"]
  Auth["Authentication Module"]
  CourseGen["Course Generation Module"]
  ContentGen["Content Generation Module"]
  Enroll["Enrollment Module"]
  Progress["Progress Tracking Module"]
  DB["Database"]
  AI["AI Service"]
  YT["YouTube API"]
  IMG["Image Generation API"]

  User -- Sign In/Up --> Auth
  Auth -- User Data --> DB
  User -- Create Course --> CourseGen
  CourseGen -- Store Course --> DB
  CourseGen -- Send Prompt --> AI
  AI -- Course Layout --> CourseGen
  CourseGen -- Banner Prompt --> IMG
  IMG -- Banner Image --> CourseGen
  User -- Edit Course --> ContentGen
  ContentGen -- Store Content --> DB
  ContentGen -- Send Chapters --> AI
  AI -- Content JSON --> ContentGen
  ContentGen -- Get Videos --> YT
  YT -- Video Links --> ContentGen
  User -- Enroll Course --> Enroll
  Enroll -- Save Enrollment --> DB
  User -- View Course/Progress --> Progress
  Progress -- Update Progress --> DB
```

## DFD-2 (Detailed Data Flows)

```mermaid
flowchart TD
  subgraph User Actions
    U1["Sign Up/Sign In"]
    U2["Create Course"]
    U3["Edit Course"]
    U4["Enroll Course"]
    U5["View Course/Progress"]
  end

  subgraph Backend Modules
    Auth["Authentication"]
    CourseGen["Course Generation"]
    ContentGen["Content Generation"]
    Enroll["Enrollment"]
    Progress["Progress Tracking"]
  end

  subgraph External Services
    AI["AI Service"]
    YT["YouTube API"]
    IMG["Image Generation API"]
  end

  DB["Database"]

  U1 --> Auth
  Auth -- User Data --> DB
  U2 --> CourseGen
  CourseGen -- Store Course --> DB
  CourseGen -- Send Prompt --> AI
  AI -- Course Layout --> CourseGen
  CourseGen -- Banner Prompt --> IMG
  IMG -- Banner Image --> CourseGen
  U3 --> ContentGen
  ContentGen -- Store Content --> DB
  ContentGen -- Send Chapters --> AI
  AI -- Content JSON --> ContentGen
  ContentGen -- Get Videos --> YT
  YT -- Video Links --> ContentGen
  U4 --> Enroll
  Enroll -- Save Enrollment --> DB
  U5 --> Progress
  Progress -- Update Progress --> DB
```

## Use Case Diagram

```mermaid
%% UML Use Case Diagram with stickman actor
usecaseDiagram
  actor User as "User"
  User --> (Sign In/Up)
  User --> (Create Course (AI))
  User --> (Edit Course)
  User --> (Generate Course Content (AI))
  User --> (Enroll in Course)
  User --> (View Course)
  User --> (Track Progress)

  (Sign In/Up) --> (Dashboard / Workspace)
  (Dashboard / Workspace) --> (Create Course (AI))
  (Dashboard / Workspace) --> (Edit Course)
  (Dashboard / Workspace) --> (Enroll in Course)
  (Dashboard / Workspace) --> (View Course)

  (Create Course (AI)) --> (Generate Course Content (AI))
  (Create Course (AI)) --> (Banner Image Generation)
  (Generate Course Content (AI)) --> (Get Videos)
  (Generate Course Content (AI)) --> (Save Content)
  (Enroll in Course) --> (Save Enrollment)
  (View Course) --> (Track Progress)
```

## Sequence Diagram

```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend
  participant BE as Backend
  participant AI as AI Service
  participant DB as Database
  participant IMG as Image API
  participant YT as YouTube API

  U->>FE: Sign Up / Sign In
  FE->>BE: Auth Request
  BE->>DB: Check/Create User
  DB-->>BE: User Data
  BE-->>FE: Auth Success

  U->>FE: Create Course (details)
  FE->>BE: POST /api/generate-course-layout
  BE->>AI: Send Prompt
  AI-->>BE: Course Layout JSON
  BE->>IMG: Generate Banner Image
  IMG-->>BE: Banner Image URL
  BE->>DB: Save Course
  DB-->>BE: Course Saved
  BE-->>FE: Course Created

  U->>FE: Edit Course
  FE->>BE: GET /api/course?courseId
  BE->>DB: Fetch Course
  DB-->>BE: Course Data
  BE-->>FE: Course Data

  U->>FE: Generate Content
  FE->>BE: POST /api/generate-course-content
  BE->>AI: Send Chapter Prompts
  AI-->>BE: Content JSON
  BE->>YT: Search Videos
  YT-->>BE: Video Links
  BE->>DB: Save Content
  DB-->>BE: Content Saved
  BE-->>FE: Content Ready

  U->>FE: Enroll Course
  FE->>BE: POST /api/enroll-course
  BE->>DB: Save Enrollment
  DB-->>BE: Enrollment Saved
  BE-->>FE: Enrolled

  U->>FE: View Course
  FE->>BE: GET /api/enroll-course?courseId
  BE->>DB: Fetch Enrollment & Content
  DB-->>BE: Data
  BE-->>FE: Course Content

  U->>FE: Mark Chapter Complete
  FE->>BE: PUT /api/enroll-course
  BE->>DB: Update Progress
  DB-->>BE: Progress Updated
  BE-->>FE: Progress Updated
```

## Gantt Chart

```mermaid
gantt
dateFormat  YYYY-MM-DD
section Requirements & Analysis
Collect User Requirements      :done,    reqs, 2024-06-01, 14d
System Analysis                :done,    analysis, after reqs, 3d
section Design
System Design                  :done,    design, after analysis, 3d
section Implementation
Auth Module                    :active,  auth, 2024-06-18, 5d
Course Generation Module       :active,  coursegen, after auth, 5d
Content Generation Module      :active,  contentgen, after coursegen, 5d
Enrollment Module              :active,  enroll, after contentgen, 3d
Progress Tracking              :active,  progress, after enroll, 2d
UI/UX Components               :active,  uiux, after progress, 5d
API Integrations               :active,  apiint, after uiux, 3d
Database Schema                :active,  db, after apiint, 2d
section Testing & Deployment
Testing                        :         test, after db, 4d
Deployment                     :         deploy, after test, 2d
```

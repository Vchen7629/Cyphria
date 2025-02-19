import { lazy } from "react"
import { Routes, Route } from "react-router"

const Homepage = lazy(() => (import("./pages/homepage.tsx")))
const Searchpage = lazy(() => (import("./pages/searchpage.tsx")))
const TemporalAnalysisPage = lazy(() => (import("./pages/temporalanalysispage.tsx")))
const Bookmarkpage = lazy(() => (import("./pages/bookmarkpage.tsx")))
const Profilepage = lazy(() => (import("./pages/profilepage.tsx")))

function App() {

  return (
    <Routes>
      <Route path="" element={<Homepage/>}/>
      <Route path="/search" element={<Searchpage/>}/>
      <Route path="/temporal" element={<TemporalAnalysisPage/>}/>
      <Route path="/bookmarks" element={<Bookmarkpage/>}/>
      <Route path="/profile" element={<Profilepage/>}/>
    </Routes>
  )
}

export default App

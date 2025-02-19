import { lazy } from "react"
import { Routes, Route } from "react-router"

const Homepage = lazy(() => (import("./pages/homepage.tsx")))

function App() {

  return (
    <Routes>
      <Route path="" element={<Homepage/>}/>
    </Routes>
  )
}

export default App

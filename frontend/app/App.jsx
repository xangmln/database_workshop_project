import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import RootLayout from "./pages/Root.jsx";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    id: "root",
    children: [
      { index: true , element: <Home /> },
      { path: "auth", element: <Login /> },
    ],
  },
]);

function App() {
    return <RouterProvider router={router} />
}

export default App;
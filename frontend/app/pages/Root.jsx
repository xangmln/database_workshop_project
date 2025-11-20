import { Outlet } from "react-router-dom";
import MainNavigation from "../components/MainNavigation";

import MainLayout from "./Main";

function RootLayout() {
  return (
    <>
      <MainLayout>
        <MainNavigation></MainNavigation>
        <Outlet />
      </MainLayout>
    </>
  );
}

export default RootLayout;

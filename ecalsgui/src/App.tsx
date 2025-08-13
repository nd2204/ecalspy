import "./App.css";
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label";
import { ThemeProvider } from "@/components/theme-provider";
import { SidebarLayout } from "@/layouts/sidebar-layout"
import { LoginForm } from "@/components/login-form"

import { BrowserRouter, Routes, Route, Link } from "react-router-dom"

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <SidebarLayout>
        <div className="grid auto-rows-min gap-4 md:grid-cols-3">
          <div className="bg-muted/50 aspect-video rounded-xl" />
          <div className="bg-muted/50 aspect-video rounded-xl" />
          <div className="bg-muted/50 aspect-video rounded-xl" />
        </div>
        <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min" />
      </SidebarLayout>
    </ThemeProvider >
  );
}

export default App;

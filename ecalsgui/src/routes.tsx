import {
  Calendar,
  ChevronUp,
  Home,
  Settings,
  User2,
  LucideIcon
} from "lucide-react"

import { JSX } from "react/jsx-runtime";

export const ROUTE_PATHS = {
  HOME: "/",
  CALENDAR: "/calendar",
  SETTINGS: "/settings",
  NOT_FOUND: "*",
} as const;

export interface AppRoute {
  path: string;
  element: JSX.Element;
}

export interface SidebarRoutes {
  path: string;
  title: string;
  icon?: LucideIcon;
}

export const appRoutes: AppRoute[] = [
  {
    path: ROUTE_PATHS.HOME,
    element: <div />,
  },
  {
    path: ROUTE_PATHS.NOT_FOUND,
    element: <div />,
  },
  {
    path: ROUTE_PATHS.CALENDAR,
    element: <div />,
  },
  {
    path: ROUTE_PATHS.SETTINGS,
    element: <div />,
  }
];

export const sidebarRoutes: SidebarRoutes[] = [
  {
    title: "Home",
    path: ROUTE_PATHS.HOME,
    icon: Home,
  },
  {
    title: "Calendar",
    path: ROUTE_PATHS.CALENDAR,
    icon: Calendar,
  },
  {
    title: "Settings",
    path: ROUTE_PATHS.SETTINGS,
    icon: Settings
  }
] as const

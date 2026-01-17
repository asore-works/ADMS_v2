"use client";

import {
  CalendarIcon,
  ClipboardListIcon,
  FileTextIcon,
  FolderIcon,
  HomeIcon,
  PlaneIcon,
  SettingsIcon,
  UsersIcon,
  WrenchIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useCurrentUser } from "@/stores/auth";

const mainMenuItems = [
  {
    title: "ダッシュボード",
    url: "/dashboard",
    icon: HomeIcon,
  },
  {
    title: "フライトログ",
    url: "/flights",
    icon: PlaneIcon,
  },
  {
    title: "飛行申請",
    url: "/applications",
    icon: FileTextIcon,
  },
  {
    title: "プロジェクト",
    url: "/projects",
    icon: FolderIcon,
  },
  {
    title: "スケジュール",
    url: "/schedule",
    icon: CalendarIcon,
  },
];

const managementMenuItems = [
  {
    title: "機体管理",
    url: "/equipment",
    icon: PlaneIcon,
  },
  {
    title: "スタッフ",
    url: "/staff",
    icon: UsersIcon,
  },
  {
    title: "メンテナンス",
    url: "/maintenance",
    icon: WrenchIcon,
  },
  {
    title: "カタログ",
    url: "/catalogs",
    icon: ClipboardListIcon,
  },
];

const settingsMenuItems = [
  {
    title: "設定",
    url: "/settings",
    icon: SettingsIcon,
  },
];

export function AppSidebar() {
  const pathname = usePathname();
  const user = useCurrentUser();

  const isActive = (url: string) => pathname === url || pathname.startsWith(`${url}/`);

  return (
    <Sidebar>
      <SidebarHeader className="border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <PlaneIcon className="h-6 w-6" />
          <span className="text-lg font-semibold">ADMS</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>メイン</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainMenuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>管理</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {managementMenuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {settingsMenuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t p-4">
        {user && (
          <div className="text-sm">
            <p className="font-medium">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-muted-foreground">{user.email}</p>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}

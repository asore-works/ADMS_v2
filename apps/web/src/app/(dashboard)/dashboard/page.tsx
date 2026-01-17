"use client";

import { CalendarIcon, FileTextIcon, PlaneIcon, UsersIcon } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCurrentUser } from "@/stores/auth";

interface StatCardProps {
  title: string;
  value: string | number;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  loading?: boolean;
}

function StatCard({ title, value, description, icon: Icon, loading }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="text-muted-foreground h-4 w-4" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <>
            <Skeleton className="mb-1 h-8 w-20" />
            <Skeleton className="h-4 w-32" />
          </>
        ) : (
          <>
            <div className="text-2xl font-bold">{value}</div>
            <p className="text-muted-foreground text-xs">{description}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const user = useCurrentUser();

  // TODO: Replace with actual data from API
  const stats = [
    {
      title: "総フライト数",
      value: "0",
      description: "今月のフライト",
      icon: PlaneIcon,
    },
    {
      title: "登録機体数",
      value: "0",
      description: "アクティブな機体",
      icon: PlaneIcon,
    },
    {
      title: "スタッフ数",
      value: "0",
      description: "アクティブなスタッフ",
      icon: UsersIcon,
    },
    {
      title: "申請中",
      value: "0",
      description: "承認待ちの申請",
      icon: FileTextIcon,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ダッシュボード</h1>
        {user && (
          <p className="text-muted-foreground">
            おかえりなさい、{user.first_name} {user.last_name}さん
          </p>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            description={stat.description}
            icon={stat.icon}
          />
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              今日の予定
            </CardTitle>
            <CardDescription>本日のフライトスケジュール</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">予定はありません</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileTextIcon className="h-5 w-5" />
              最近のアクティビティ
            </CardTitle>
            <CardDescription>最新のフライトログと申請</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">アクティビティはありません</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

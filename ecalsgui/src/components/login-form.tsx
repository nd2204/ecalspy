import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Đăng nhập vào tài khoản sinh viên</CardTitle>
          <CardDescription>
            Nhập mã sinh viên, mật khẩu, captcha để đăng nhập vào tài khoản sinh viên
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form>
            <div className="flex flex-col gap-6">
              <div className="grid gap-3">
                <Label htmlFor="login_id">Mã sinh viên</Label>
                <Input
                  id="login_id"
                  type="text"
                  placeholder="vd: 11122233344"
                  required
                />
              </div>
              <div className="grid gap-3">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                </div>
                <Input id="password" type="password" required />
              </div>
              <div className="grid gap-3">
                <div className="flex items-center">
                  <Label htmlFor="captcha">Nhập mã bảo vệ</Label>
                </div>
                <Input id="captcha" type="text" required />
                <img
                  src="https://thanhtoanhocphi.epu.edu.vn/WebCommon/GetCaptcha"
                  className=""
                  alt=""
                />
              </div>
              <Separator />
              <div className="flex flex-col gap-3">
                <Button type="submit" className="w-full">
                  Đăng nhập
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

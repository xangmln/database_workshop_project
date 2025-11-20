import AuthForm from "../components/AuthForm";
import { redirect } from "react-router-dom";

export default function Login() {
  return <AuthForm/>;
}

export async function action({ request }) {
  console.log(request.url);
  const searchParams = new URL(request.url).searchParams;
  const mode = searchParams.get("mode") || "login";

  if (mode !== "login" && mode !== "signup") {
    throw new Response(JSON.stringify({ message: "Unsupported mode" }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
  const data = await request.formData();
  const authData = {
    email: data.get("email"),
    password: data.get("password"),
    username: data.get("userName"),
  };

  const response = await fetch(`${API_BASE}/auth/` + mode, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(authData),
  });

  // authform에서 useActionData 훅으로 오류를 폼 안에서 생성.
  if (response.status === 422 || response.status === 401) {
    return response;
  }

  if (response.status === 404) {
    throw json(
      { message: "OOOOOOOOOOOOOOOOOOOO" },
      {
        status: 400,
        statusText: "Could not register",
      }
    );
  }

  if (!response.ok) {
    throw new Response(null, {
      status: 500,
      statusText: "Could not authenticate user.",
    });
  }

  const resData = await response.json();
  const token = resData.data.access_token;

  // 2.mode가 login일때만 localStorage에 token을 저장해서 로그인하고
  // 2. signup일 경우에는 백엔드에 토큰생성 전송은 하되 로그인을 해야지만 토큰이 localStorage저장되어서 / url로 넘어가는 동작을 구현하고싶어.
  if (mode === "login") {
    localStorage.setItem("token", token);
    return redirect("/");
  } else {
    return redirect("/auth?mode=login&message=signup-success");
  }
}

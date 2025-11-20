import { useEffect } from "react";
import {
  Form,
  Link,
  useSearchParams,
  useActionData,
  useNavigation,
} from "react-router-dom";

function AuthForm() {
  const data = useActionData();
  const navigation = useNavigation();
  const [searchParams] = useSearchParams();
  const isLogin = searchParams.get("mode") === "login";
  const message = searchParams.get("message");
  const isSubmitting = navigation.state === "submitting";

  useEffect(() => {
    if (message === "signup-success") {
      alert("회원가입이 완료되었습니다. 로그인 페이지로 이동합니다.");
      window.location.href = "/auth?mode=login";
    }
  }, [message]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {isLogin ? "로그인" : "회원가입"}
              </h1>
              <p className="text-gray-600">
                {isLogin ? "로그인 되었습니다." : "지금 계정을 생성하세요"}
              </p>
            </div>

            <Form method="post" className="space-y-6">
              {data?.errors && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                  <ul className="text-sm text-red-700">
                    {Object.values(data.errors).map((err, index) => (
                      <li key={index} className="flex items-center">
                        <span className="mr-2">⚠️</span>
                        {err}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {data?.message && (
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
                  <p className="text-yellow-700">{data.message}</p>
                </div>
              )}

              {!isLogin && (
                <div>
                  <label
                    htmlFor="username"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    사용자 이름
                  </label>
                  <input
                    id="username"
                    type="text"
                    name="userName"
                    required
                    className="text-black w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-transparent transition duration-200"
                    placeholder="사용자 이름을 입력하세요"
                  />
                </div>
              )}

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  이메일
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  required
                  className="text-black w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-transparent transition duration-200"
                  placeholder="이메일을 입력하세요"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  비밀번호
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  required
                  className="text-black w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-transparent transition duration-200"
                  placeholder="비밀번호를 입력하세요 (8자리 이상)"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`w-full py-3 px-4 rounded-lg font-medium text-white ${
                    isSubmitting
                      ? "bg-red-400 cursor-not-allowed"
                      : "bg-[#C20E2F] hover:bg-red-700"
                  } transition duration-200 flex items-center justify-center`}
                >
                  {isSubmitting ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      처리 중...
                    </>
                  ) : isLogin ? (
                    "로그인"
                  ) : (
                    "회원가입"
                  )}
                </button>
              </div>

              <div className="text-center text-sm text-gray-600 pt-2">
                {isLogin ? "계정이 없으신가요? " : "이미 계정이 있으신가요? "}
                <Link
                  to={`?mode=${isLogin ? "signup" : "login"}`}
                  className="font-medium text-[#C20E2F] hover:text-red-500 transition-colors"
                >
                  {isLogin ? "회원가입" : "로그인"} 하기
                </Link>
              </div>
            </Form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthForm;

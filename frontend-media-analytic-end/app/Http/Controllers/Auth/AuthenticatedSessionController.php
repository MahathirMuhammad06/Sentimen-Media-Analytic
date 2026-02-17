<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Http\Requests\Auth\LoginRequest;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\View\View;

class AuthenticatedSessionController extends Controller
{
    /**
     * Display the login view.
     */
    public function create(): View
    {
        return view('auth.login');
    }

    /**
     * Handle an incoming authentication request.
     */
public function store(LoginRequest $request)
{
    $request->authenticate();

    $request->session()->regenerate();

    // 🔥 HAPUS MODE GUEST SAAT LOGIN
    $request->session()->forget('is_guest');

    return redirect()->intended(route('dashboard'));
}



    /**
     * Destroy an authenticated session.
     */
public function destroy(Request $request): RedirectResponse
{
    Auth::guard('web')->logout();

    // Hapus guest juga
    $request->session()->forget('is_guest');

    $request->session()->invalidate();

    $request->session()->regenerateToken();

    return redirect()->route('login');
}

}

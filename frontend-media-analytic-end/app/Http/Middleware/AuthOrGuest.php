<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Session;

class AuthOrGuest
{
public function handle(Request $request, Closure $next)
{
    // Jika sudah login → PRIORITAS
    if (Auth::check()) {
        return $next($request);
    }

    // Jika belum login tapi guest
    if (session()->get('is_guest') === true) {
        return $next($request);
    }

    return redirect()->route('login');
}

}

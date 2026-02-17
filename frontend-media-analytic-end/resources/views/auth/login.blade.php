<x-guest-layout>

    {{-- Header / Branding --}}
    <div class="text-center mb-8">

        {{-- Logo --}}
        <img src="{{ asset('images/logo-siger-bandarlampung.png') }}"
             alt="MEDAL Logo"
             class="h-40 mx-auto mb-3 drop-shadow-sm">

        {{-- Title --}}
        <h1 class="text-2xl font-bold text-gray-800">
            MEDAL
        </h1>

        {{-- Subtitle --}}
        <p class="text-sm text-gray-500 mt-1">
            News Sentiment Analytics
        </p>

    </div>


    <!-- Session Status -->
    <x-auth-session-status
        class="mb-4 text-sm text-center"
        :status="session('status')"
    />


    <form method="POST" action="{{ route('login') }}" class="space-y-4">
        @csrf


        <!-- Email -->
        <div>
            <x-input-label
                for="email"
                :value="__('Email Address')"
                class="text-sm font-medium"
            />

            <x-text-input
                id="email"
                class="block mt-1 w-full rounded-lg focus:ring-2 focus:ring-indigo-500"
                type="email"
                name="email"
                :value="old('email')"
                required
                autofocus
                autocomplete="username"
                placeholder="you@example.com"
            />

            <x-input-error
                :messages="$errors->get('email')"
                class="mt-1 text-sm"
            />
        </div>


        <!-- Password -->
        <div>
            <x-input-label
                for="password"
                :value="__('Password')"
                class="text-sm font-medium"
            />

            <x-text-input
                id="password"
                class="block mt-1 w-full rounded-lg focus:ring-2 focus:ring-indigo-500"
                type="password"
                name="password"
                required
                autocomplete="current-password"
                placeholder="••••••••"
            />

            <x-input-error
                :messages="$errors->get('password')"
                class="mt-1 text-sm"
            />
        </div>


        <!-- Remember & Forgot -->
        <div class="flex items-center justify-between text-sm">

            <label for="remember_me" class="inline-flex items-center">
                <input
                    id="remember_me"
                    type="checkbox"
                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    name="remember"
                >
                <span class="ml-2 text-gray-600">
                    Remember me
                </span>
            </label>

            @if (Route::has('password.request'))
                <a
                    href="{{ route('password.request') }}"
                    class="text-indigo-600 hover:underline font-medium"
                >
                    Forgot password?
                </a>
            @endif

        </div>


        <!-- Buttons -->
        <div class="flex flex-col gap-3 pt-4">


            {{-- Login --}}
            <x-primary-button
                class="w-full justify-center py-3 text-base font-semibold rounded-lg"
            >
                Sign In
            </x-primary-button>


            {{-- Guest --}}
            <a href="{{ route('guest.login') }}"
               class="w-full text-center py-3 bg-gray-100 text-gray-700
                      rounded-lg font-medium
                      hover:bg-gray-200 transition">

                Continue as Guest
            </a>


            {{-- Register --}}
            @if (Route::has('register'))
                <a href="{{ route('register') }}"
                   class="w-full text-center py-3 border border-indigo-600
                          text-indigo-600 rounded-lg font-medium
                          hover:bg-indigo-600 hover:text-white transition">

                    Create New Account
                </a>
            @endif


        </div>

    </form>

</x-guest-layout>

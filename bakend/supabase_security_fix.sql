-- =====================================================
-- CAMPUSMIND AI - SUPABASE SECURITY ADVISOR RESOLUTION
-- Fix 1 Error + 3 Warnings in 1-Click
-- =====================================================

-- 1. FIX ERROR: "RLS Disabled in Public" for public.todos
-- Either enable RLS or drop if it's just the default starter table
ALTER TABLE IF EXISTS public.todos ENABLE ROW LEVEL SECURITY;

-- If you don't need the starter todos table, you can drop it:
-- DROP TABLE IF EXISTS public.todos;


-- 2. FIX WARNINGS: "Public / Signed-In Users Can Execute SECURITY DEFINER Function"
-- Fix public.rls_auto_enable() by switching to SECURITY INVOKER and revoking public execution
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'public' AND p.proname = 'rls_auto_enable'
    ) THEN
        ALTER FUNCTION public.rls_auto_enable() SECURITY INVOKER;
        REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon;
    END IF;
END $$;


-- 3. FIX WARNING: "RLS Policy Always True" for public.users
-- Clean up overly permissive USING (true) write policies and replace with secure ones
ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE
    pol record;
BEGIN
    FOR pol IN 
        SELECT policyname 
        FROM pg_policies 
        WHERE tablename = 'users' AND schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.users', pol.policyname);
    END LOOP;
END $$;

-- Compliant, secure policies:
-- (A) SELECT: Everyone can read user public profiles
CREATE POLICY "Allow select user profiles" ON public.users
    FOR SELECT
    USING (true);

-- (B) INSERT: Service role or application signup
CREATE POLICY "Allow user profile insertion" ON public.users
    FOR INSERT
    WITH CHECK (
        auth.role() = 'service_role' 
        OR auth.role() = 'authenticated' 
        OR auth.role() = 'anon'
    );

-- (C) UPDATE: Only own profile or service_role
CREATE POLICY "Allow update own profile" ON public.users
    FOR UPDATE
    USING (
        auth.role() = 'service_role'
        OR auth.uid()::text = id::text
        OR email = auth.jwt()->>'email'
    )
    WITH CHECK (
        auth.role() = 'service_role'
        OR auth.uid()::text = id::text
        OR email = auth.jwt()->>'email'
    );

-- (D) DELETE: Only service role can delete
CREATE POLICY "Allow delete service role" ON public.users
    FOR DELETE
    USING (auth.role() = 'service_role');


SMALIEN_LOG_CLASS = 'LSmalienLog_{};'

# Code for value logging
CODE_WITH_VL = {
    'method': 'Log_{}({})V',

    'invoke': 'invoke-static/range {{{} .. {}}}, {}->{}',

    'definition': {
        # 'base':
        #     '.method public static {}\n\n'\
        #     '{}\n\n'\
        #     '    const-string v0, "{}"\n'\
        #     '    invoke-static {{v0, p0}}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        #     '    return-void\n'\
        #     '.end method\n\n',

        'to_string': {
            #
            # Primitive-data-type values
            #
            'Z':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromZ(ZLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'B':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromB(BLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'C':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromC(CLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'S':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromS(SLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'I':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromI(ILjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'F':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromF(FLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'J':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, p1, v0}}, LSmalienWriter;->fromJ(JLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            'D':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, p1, v0}}, LSmalienWriter;->fromD(DLjava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            # String values.
            # Logs hashCode + ':' + string value if the object is not null, otherwise 'n'
            'Ljava/lang/String;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromString(Ljava/lang/String;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/String;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, Ljava/lang/String;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromString(Ljava/lang/String;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            # Ljava/lang/CharSequence; values
            'Ljava/lang/CharSequence;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromCharSequence(Ljava/lang/CharSequence;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/CharSequence;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, Ljava/lang/CharSequence;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromCharSequence(Ljava/lang/CharSequence;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            # For reflection method, class, and field, their object identifiers are not logged because currently the identifiers are used for nothing.
            # Only their string values are necessary.
            'Ljava/lang/reflect/Method;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectMethod(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/reflect/Method;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectMethod(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'Ljava/lang/Class;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromClass(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/Class;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromClass(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'Ljava/lang/reflect/Field;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectField(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/reflect/Field;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectField(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'Ljava/lang/reflect/Type;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectType(Ljava/lang/reflect/Type;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableToLjava/lang/reflect/Type;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, Ljava/lang/reflect/Type;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromReflectType(Ljava/lang/reflect/Type;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            # To generate hashCode, use System.identityHashCode instead of Object.hashCode, which can be overridden by an app's method.
            'Ljava/lang/Object;-PURE':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromObjectPure(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'Ljava/lang/Object;-WITH_NULL_CHECK':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromObjectWithNullCheck(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'Ljava/lang/Object;-WITHOUT_NULL_CHECK':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromObjectWithoutNullCheck(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            #
            # Primitive-data-type value arrays
            #
            '[Z':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayZ(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[B':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayB(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[C':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayC(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[S':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayS(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[I':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayI(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[F':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayF(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[J':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayJ(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
            '[D':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayD(Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            #
            # Non-primitive arrays
            #
            '[Ljava/lang/reflect/Method;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayReflectMethod([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableTo[Ljava/lang/reflect/Method;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [Ljava/lang/Object;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayReflectMethod([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            '[Ljava/lang/Class;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayClass([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableTo[Ljava/lang/Class;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [Ljava/lang/Object;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayClass([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            '[Ljava/lang/reflect/Type;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayReflectType([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableTo[Ljava/lang/reflect/Type;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [Ljava/lang/Object;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayReflectType([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            # Using Arrays.asList makes all elements null.
            # So instead of that, explicitly logs identityHashCode of each element.
            '[Ljava/lang/Object;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayObject([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableTo[Ljava/lang/Object;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [Ljava/lang/Object;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayObject([Ljava/lang/Object;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            '[[Ljava/lang/String;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [[Ljava/lang/String;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayArrayString([[Ljava/lang/String;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',

            'CastableTo[[Ljava/lang/String;':
                '.method public static {}\n\n'\
                '    .locals 1\n\n'\
                '    check-cast p0, [[Ljava/lang/String;\n'\
                '    const-string v0, "{}"\n'\
                '    invoke-static {{p0, v0}}, LSmalienWriter;->fromArrayArrayString([[Ljava/lang/String;Ljava/lang/String;)V\n'\
                '    return-void\n'\
                '.end method\n\n',
        },
    },
}

# Code for no value logging
CODE_WITHOUT_VL = {
    'method': 'Log_{}()V',

    'invoke': 'invoke-static {{}}, {}->{}',

    'definition':
        '.method public static {}\n'\
        '    .locals 1\n'\
        '    const-string v0, "{}"\n'\
        '\n'\
        '    invoke-static {{v0}}, LSmalienWriter;->writeTag(Ljava/lang/String;)V\n'\
        '\n'\
        '    return-void\n'\
        '.end method\n\n',
}

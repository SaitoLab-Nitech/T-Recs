
# Code for converting values to strings.
TO_STRING_CONVERTERS = {
    #
    # Primitive-data-type values
    #
    'Z':
        '\n.method public static fromZ(ZLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(Z)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'B':
        '\n.method public static fromB(BLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/Byte;->toString(B)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'C':
        '\n.method public static fromC(CLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(C)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'S':
        '\n.method public static fromS(SLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'I':
        '\n.method public static fromI(ILjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'F':
        '\n.method public static fromF(FLjava/lang/String;)V\n'\
        '    .locals 2\n\n'\
        '    float-to-double v0, p0\n'\
        '    invoke-static {v0, v1}, Ljava/lang/String;->valueOf(D)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'J':
        '\n.method public static fromJ(JLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0, p1}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p2, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    'D':
        '\n.method public static fromD(DLjava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0, p1}, Ljava/lang/String;->valueOf(D)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p2, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    # String values.
    # Logs hashCode + ':' + string value if the object is not null, otherwise 'n'
    'Ljava/lang/String;':
        '\n.method public static fromString(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    .locals 2\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result v1\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    const-string v1, ":"\n'\
        '\n'\
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    # Ljava/lang/CharSequence; values
    'Ljava/lang/CharSequence;':
        '\n.method public static fromCharSequence(Ljava/lang/CharSequence;Ljava/lang/String;)V\n'\
        '    .locals 2\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result v1\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    const-string v1, ":"\n'\
        '\n'\
        '    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    # For reflection method, class, and field, their object identifiers are not logged because currently the identifiers are used for nothing.
    # Only their string values are necessary.
    'Ljava/lang/reflect/Method;':
        '\n.method public static fromReflectMethod(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    'Ljava/lang/Class;':
        '\n.method public static fromClass(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    'Ljava/lang/reflect/Field;':
        '\n.method public static fromReflectField(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    'Ljava/lang/reflect/Type;':
        '\n.method public static fromReflectType(Ljava/lang/reflect/Type;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    invoke-interface {p0}, Ljava/lang/reflect/Type;->getTypeName()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    # To generate hashCode, use System.identityHashCode instead of Object.hashCode, which can be overridden by an app's method.
    'Ljava/lang/Object;-PURE':
        '\n.method public static fromObjectPure(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    :try_start_0\n'\
        '    check-cast p0, [B\n'\
        '    :try_end_0\n'\
        '    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([B)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '    const/16 p0, 0x42\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :catch_0\n'\
        '    move-exception v0\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result p0\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    'Ljava/lang/Object;-WITH_NULL_CHECK':
        '\n.method public static fromObjectWithNullCheck(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result p0\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    'Ljava/lang/Object;-WITHOUT_NULL_CHECK':
        '\n.method public static fromObjectWithoutNullCheck(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    invoke-static {p0}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result p0\n'\
        '\n'\
        '    new-instance v0, Ljava/lang/StringBuilder;\n'\
        '    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    #
    # Primitive-data-type value arrays
    #
    '[Z':
        '\n.method public static fromArrayZ(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [Z\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([Z)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[B':
        '\n.method public static fromArrayB(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [B\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([B)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[C':
        '\n.method public static fromArrayC(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [C\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([C)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[S':
        '\n.method public static fromArrayS(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [S\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([S)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[I':
        '\n.method public static fromArrayI(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [I\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([I)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[F':
        '\n.method public static fromArrayF(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [F\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([F)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[J':
        '\n.method public static fromArrayJ(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [J\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([J)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
    '[D':
        '\n.method public static fromArrayD(Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 0\n\n'\
        '    check-cast p0, [D\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->toString([D)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    #
    # Non-primitive arrays
    #
    '[Ljava/lang/reflect/Method;':
        '\n.method public static fromArrayReflectMethod([Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    new-instance v0, Lorg/json/JSONArray;\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;\n'\
        '    move-result-object p0\n'\
        ' \n'\
        '    invoke-direct {v0, p0}, Lorg/json/JSONArray;-><init>(Ljava/util/Collection;)V\n'\
        ' \n'\
        '    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    '[Ljava/lang/Class;':
        '\n.method public static fromArrayClass([Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    new-instance v0, Lorg/json/JSONArray;\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;\n'\
        '    move-result-object p0\n'\
        ' \n'\
        '    invoke-direct {v0, p0}, Lorg/json/JSONArray;-><init>(Ljava/util/Collection;)V\n'\
        ' \n'\
        '    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    '[Ljava/lang/reflect/Type;':
        '\n.method public static fromArrayReflectType([Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    new-instance v0, Lorg/json/JSONArray;\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;\n'\
        '    move-result-object p0\n'\
        ' \n'\
        '    invoke-direct {v0, p0}, Lorg/json/JSONArray;-><init>(Ljava/util/Collection;)V\n'\
        ' \n'\
        '    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    # Using Arrays.asList makes all elements null.
    # So instead of that, explicitly logs identityHashCode of each element.
    '[Ljava/lang/Object;':
        '\n.method public static fromArrayObject([Ljava/lang/Object;Ljava/lang/String;)V\n'\
        '    .locals 5\n\n'\
        '    if-eqz p0, :cond_0\n'\
        '\n'\
        '    const-string v0, "["\n'\
        '\n'\
        '    array-length v1, p0\n'\
        '\n'\
        '    const/4 v2, 0x0\n'\
        '\n'\
        '    :goto_0\n'\
        '    if-ge v2, v1, :cond_1\n'\
        '\n'\
        '    aget-object v4, p0, v2\n'\
        '\n'\
        '    new-instance v3, Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-static {v4}, Ljava/lang/System;->identityHashCode(Ljava/lang/Object;)I\n'\
        '    move-result v4\n'\
        '\n'\
        '    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object v0\n'\
        '\n'\
        '    new-instance v3, Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    const/16 v4, 0x2c\n'\
        '\n'\
        '    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object v0\n'\
        '\n'\
        '    add-int/lit8 v2, v2, 0x1\n'\
        '\n'\
        '    goto :goto_0\n'\
        '\n'\
        '    :cond_1\n'\
        '    new-instance p0, Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V\n'\
        '\n'\
        '    if-eqz v2, :cond_2\n'\
        '\n'\
        '    invoke-virtual {v0}, Ljava/lang/String;->length()I\n'\
        '    move-result v1\n'\
        '\n'\
        '    const/4 v2, 0x1\n'\
        '\n'\
        '    sub-int/2addr v1, v2\n'\
        '\n'\
        '    const/4 v2, 0x0\n'\
        '\n'\
        '    invoke-virtual {v0, v2, v1}, Ljava/lang/String;->substring(II)Ljava/lang/String;\n'\
        '    move-result-object v0\n'\
        '\n'\
        '    :cond_2\n'\
        '\n'\
        '    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    const/16 v2, 0x5d\n'\
        '\n'\
        '    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;\n'\
        '\n'\
        '    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    goto :goto_1\n'\
        '\n'\
        '    :cond_0\n'\
        '    const-string p0, "n"\n'\
        '\n'\
        '    :goto_1\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',

    '[[Ljava/lang/String;':
        '\n.method public static fromArrayArrayString([[Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    .locals 1\n\n'\
        '    check-cast p0, [[Ljava/lang/String;\n'\
        '\n'\
        '    new-instance v0, Lorg/json/JSONArray;\n'\
        '\n'\
        '    invoke-static {p0}, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;\n'\
        '    move-result-object p0\n'\
        '\n'\
        '    invoke-direct {v0, p0}, Lorg/json/JSONArray;-><init>(Ljava/util/Collection;)V\n'\
        '\n'\
        '    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;\n'\
        '    move-result-object p0\n'\
        '    invoke-static {p1, p0}, LSmalienWriter;->writeVal(Ljava/lang/String;Ljava/lang/String;)V\n'\
        '    return-void\n'\
        '.end method\n',
}
